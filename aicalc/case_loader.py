"""Load a saved battle scenario (cases/*.json) into a Battle + DamageBackend.

Format 1 schema: see PLAN.md and the files in cases/. Design rules:

* Loud failures. Unknown keys are errors ("curent_hp" must never become a
  silent default), every enum-ish value is validated against its known set,
  and error messages carry a JSON-path-style location.
* Canonical names only. Every move-name position is run through
  names.canonical_move, so the Battle the engine sees uses the scraped
  spellings ("ThunderPunch"), whatever the file says ("Thunder Punch").
* Damage facts are computed by the ported AI damage calculator
  (aicalc/calc/). The optional "damage" section supplies per-fact overrides
  layered on top of it -- for the two moves whose facts depend on the AI's
  internal power roll (Bulldoze, Triple Axel), for facts needing data the
  schema lacks (party movesets, weights), or to pin a fact under test.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from . import movedata
from .calc import CalcBackend, OverrideBackend
from .names import UnknownName, canonical_flag, canonical_move, squash
from .state import VOLATILES, Battle, Field, Pokemon, Side

_DATA = Path(__file__).resolve().parent.parent / "data"

FORMAT = 1

STATUSES = frozenset({"psn", "brn", "par", "slp", "frz", "tox"})
WEATHERS = frozenset({"sun", "rain", "sand", "hail", "fog"})
TYPES = frozenset({
    "Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug",
    "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic",
    "Ice", "Dragon", "Dark", "???",
})
STAT_KEYS = ("atk", "def", "spa", "spd", "spe")
BOOST_KEYS = frozenset(STAT_KEYS) | {"acc", "eva"}
HAZARDS = frozenset({"spikes", "toxic_spikes", "stealth_rock"})
EFFECTIVENESS = (0, 0.25, 0.5, 1, 2, 4)
GENDERS = frozenset({"M", "F"})


class CaseError(ValueError):
    """A scenario file problem, located by a JSON-path-style prefix."""


@dataclass
class Case:
    name: str
    battle: Battle
    damage: object  # a DamageBackend: CalcBackend, possibly override-wrapped
    source: str | None = None
    notes: tuple[str, ...] = ()
    expected: dict[str, Fraction] | None = None  # canonical move -> pick prob
    path: Path | None = None


@lru_cache(maxsize=1)
def _abilities() -> dict[str, str]:
    """squash(name) -> canonical ability name, from the Kaizo ability table."""
    out: dict[str, str] = {}
    with (_DATA / "ability_changes.csv").open() as fh:
        for row in csv.DictReader(fh):
            for col in ("Ability 1", "Ability 2"):
                name = (row.get(col) or "").strip()
                if name and name != "-":
                    out[squash(name)] = name
    return out


# --- primitive checks -------------------------------------------------------

def _dict(obj, where: str) -> dict:
    if not isinstance(obj, dict):
        raise CaseError(f"{where}: expected an object, got {type(obj).__name__}")
    return obj


def _keys(obj: dict, where: str, required: tuple[str, ...],
          optional: tuple[str, ...] = ()) -> None:
    for key in required:
        if key not in obj:
            raise CaseError(f"{where}: missing required key {key!r}")
    for key in obj:
        if key not in required and key not in optional:
            raise CaseError(f"{where}: unknown key {key!r}")


def _int(value, where: str, minimum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise CaseError(f"{where}: expected an integer, got {value!r}")
    if minimum is not None and value < minimum:
        raise CaseError(f"{where}: {value} is below the minimum of {minimum}")
    return value


def _bool(value, where: str) -> bool:
    if not isinstance(value, bool):
        raise CaseError(f"{where}: expected true/false, got {value!r}")
    return value


def _str(value, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise CaseError(f"{where}: expected a non-empty string, got {value!r}")
    return value


def _enum(value, allowed, where: str, *, nullable: bool = False):
    if value is None and nullable:
        return None
    if value not in allowed:
        options = ", ".join(sorted(str(a) for a in allowed))
        raise CaseError(f"{where}: {value!r} not one of {{{options}}}")
    return value


def _move(name, where: str) -> str:
    try:
        return canonical_move(_str(name, where))
    except UnknownName as exc:
        raise CaseError(f"{where}: {exc}") from None


# --- section parsers --------------------------------------------------------

def _pokemon(obj, where: str, *, moves_required: bool) -> Pokemon:
    obj = _dict(obj, where)
    _keys(obj, where,
          required=("species", "level", "ability", "types", "stats", "max_hp"),
          optional=("moves", "item", "current_hp", "status", "boosts",
                    "last_move", "protect_streak", "gender", "volatiles",
                    "turns_active", "moves_used", "consumed_item", "pp_left"))
    if moves_required and not obj.get("moves"):
        raise CaseError(f"{where}: 'moves' is required for the AI's Pokemon")

    ability_raw = _str(obj["ability"], f"{where}.ability")
    ability = _abilities().get(squash(ability_raw))
    if ability is None:
        raise CaseError(f"{where}.ability: unknown ability {ability_raw!r} "
                        f"(not in data/ability_changes.csv)")

    types = obj["types"]
    if not isinstance(types, list) or not types:
        raise CaseError(f"{where}.types: expected a non-empty list")
    types = tuple(_enum(t, TYPES, f"{where}.types[{i}]")
                  for i, t in enumerate(types))

    stats = _dict(obj["stats"], f"{where}.stats")
    _keys(stats, f"{where}.stats", required=STAT_KEYS)
    stats = {k: _int(stats[k], f"{where}.stats.{k}", minimum=1) for k in STAT_KEYS}

    max_hp = _int(obj["max_hp"], f"{where}.max_hp", minimum=1)
    current_hp = _int(obj.get("current_hp", max_hp), f"{where}.current_hp",
                      minimum=0)
    if current_hp > max_hp:
        raise CaseError(f"{where}.current_hp: {current_hp} exceeds max_hp {max_hp}")

    boosts = _dict(obj.get("boosts", {}), f"{where}.boosts")
    for stat, stage in boosts.items():
        _enum(stat, BOOST_KEYS, f"{where}.boosts")
        _int(stage, f"{where}.boosts.{stat}")
        if not -6 <= stage <= 6:
            raise CaseError(f"{where}.boosts.{stat}: {stage} outside -6..+6")

    volatiles = obj.get("volatiles", [])
    if not isinstance(volatiles, list):
        raise CaseError(f"{where}.volatiles: expected a list")
    volatiles = {_enum(v, VOLATILES, f"{where}.volatiles[{i}]")
                 for i, v in enumerate(volatiles)}

    moves = [_move(m, f"{where}.moves[{i}]")
             for i, m in enumerate(obj.get("moves", []))]

    pp_left = _dict(obj.get("pp_left", {}), f"{where}.pp_left")

    item = obj.get("item")
    consumed = obj.get("consumed_item")
    return Pokemon(
        species=_str(obj["species"], f"{where}.species"),
        level=_int(obj["level"], f"{where}.level", minimum=1),
        ability=ability,
        item=None if item is None else _str(item, f"{where}.item"),
        types=types,
        stats=stats,
        max_hp=max_hp,
        current_hp=current_hp,
        status=_enum(obj.get("status"), STATUSES, f"{where}.status", nullable=True),
        boosts=dict(boosts),
        moves=moves,
        last_move=(None if obj.get("last_move") is None
                   else _move(obj["last_move"], f"{where}.last_move")),
        protect_streak=_int(obj.get("protect_streak", 0),
                            f"{where}.protect_streak", minimum=0),
        gender=_enum(obj.get("gender"), GENDERS, f"{where}.gender", nullable=True),
        volatiles=volatiles,
        turns_active=_int(obj.get("turns_active", 1), f"{where}.turns_active",
                          minimum=1),
        moves_used={_move(m, f"{where}.moves_used[{i}]")
                    for i, m in enumerate(obj.get("moves_used", []))},
        consumed_item=None if consumed is None else _str(consumed,
                                                         f"{where}.consumed_item"),
        pp_left={_move(m, f"{where}.pp_left"): _int(pp, f"{where}.pp_left[{m!r}]",
                                                    minimum=0)
                 for m, pp in pp_left.items()},
    )


def _side(obj, where: str, *, moves_required: bool) -> Side:
    obj = _dict(obj, where)
    _keys(obj, where,
          required=("pokemon", "party_remaining"),
          optional=("hazards", "reflect", "light_screen", "tailwind",
                    "safeguard", "mist", "lucky_chant", "future_attack",
                    "party_statuses"))

    hazards = _dict(obj.get("hazards", {}), f"{where}.hazards")
    for hazard, layers in hazards.items():
        _enum(hazard, HAZARDS, f"{where}.hazards")
        _int(layers, f"{where}.hazards.{hazard}", minimum=0)

    statuses = obj.get("party_statuses", [])
    if not isinstance(statuses, list):
        raise CaseError(f"{where}.party_statuses: expected a list")
    statuses = [_enum(s, STATUSES, f"{where}.party_statuses[{i}]", nullable=True)
                for i, s in enumerate(statuses)]

    flags = {key: _bool(obj[key], f"{where}.{key}")
             for key in ("reflect", "light_screen", "tailwind", "safeguard",
                         "mist", "lucky_chant", "future_attack") if key in obj}
    return Side(
        active=_pokemon(obj["pokemon"], f"{where}.pokemon",
                        moves_required=moves_required),
        party_remaining=_int(obj["party_remaining"], f"{where}.party_remaining",
                             minimum=0),
        hazards=dict(hazards),
        party_statuses=statuses,
        **flags,
    )


def _field(obj, where: str) -> Field:
    obj = _dict(obj, where)
    _keys(obj, where, required=(),
          optional=("weather", "turn", "trick_room", "gravity"))
    return Field(
        weather=_enum(obj.get("weather"), WEATHERS, f"{where}.weather",
                      nullable=True),
        turn=_int(obj.get("turn", 1), f"{where}.turn", minimum=1),
        trick_room=_bool(obj.get("trick_room", False), f"{where}.trick_room"),
        gravity=_bool(obj.get("gravity", False), f"{where}.gravity"),
    )


def _flags(lst, where: str) -> set[str]:
    if not isinstance(lst, list) or not lst:
        raise CaseError(f"{where}: expected a non-empty list of flag names")
    out = set()
    for i, name in enumerate(lst):
        try:
            out.add(canonical_flag(_str(name, f"{where}[{i}]")))
        except UnknownName as exc:
            raise CaseError(f"{where}[{i}]: {exc}") from None
    return out


def _damage(obj, where: str, ai_moves: list[str]) -> OverrideBackend:
    """Per-fact overrides layered on the computed CalcBackend. Every key is
    optional; a supplied fact always wins over the computed one."""
    obj = _dict(obj, where)
    _keys(obj, where, required=(),
          optional=("moves", "best_damaging_move", "has_super_effective_move",
                    "party_member_outdamages", "target_last_move_outdamages"))

    facts = _dict(obj.get("moves", {}), f"{where}.moves")
    facts = {_move(m, f"{where}.moves"): entry for m, entry in facts.items()}
    extra = sorted(set(facts) - set(ai_moves))
    if extra:
        raise CaseError(f"{where}.moves: entry for non-AI move(s) {extra}")

    move_facts: dict[str, dict] = {}
    for move, entry in facts.items():
        entry_where = f"{where}.moves[{move!r}]"
        entry = _dict(entry, entry_where)
        _keys(entry, entry_where, required=(), optional=("can_ko", "effectiveness"))
        if not entry:
            raise CaseError(f"{entry_where}: empty override (supply can_ko "
                            f"and/or effectiveness, or drop the entry)")
        parsed: dict = {}
        if "effectiveness" in entry:
            eff = entry["effectiveness"]
            if eff not in EFFECTIVENESS:
                raise CaseError(f"{entry_where}.effectiveness: {eff!r} not in "
                                f"{{0, 0.25, 0.5, 1, 2, 4}}")
            parsed["effectiveness"] = eff
        if "can_ko" in entry:
            parsed["can_ko"] = _bool(entry["can_ko"], f"{entry_where}.can_ko")
        move_facts[move] = parsed

    best: frozenset[str] | None = None
    if "best_damaging_move" in obj:
        best_raw = obj["best_damaging_move"]
        if best_raw is None:
            best_list = []
        elif isinstance(best_raw, str):
            best_list = [best_raw]
        elif isinstance(best_raw, list):
            best_list = best_raw
        else:
            raise CaseError(f"{where}.best_damaging_move: expected a move "
                            f"name, a list of names, or null")
        best = frozenset(_move(m, f"{where}.best_damaging_move")
                         for m in best_list)
        for move in sorted(best):
            if move not in ai_moves:
                raise CaseError(f"{where}.best_damaging_move: {move!r} is not "
                                f"one of the AI's moves")
            if not movedata.is_damaging(move):
                raise CaseError(f"{where}.best_damaging_move: {move!r} is not "
                                f"a damaging move")

    def _opt_bool(key):
        return (_bool(obj[key], f"{where}.{key}") if key in obj else None)

    return OverrideBackend(
        CalcBackend(),
        move_facts=move_facts,
        best=best,
        has_super_effective=_opt_bool("has_super_effective_move"),
        party_outdamages=_opt_bool("party_member_outdamages"),
        last_move_outdamages=_opt_bool("target_last_move_outdamages"),
    )


def _expected(obj, where: str, ai_moves: list[str]) -> dict[str, Fraction]:
    obj = _dict(obj, where)
    _keys(obj, where, required=("pick_probabilities",))
    picks = _dict(obj["pick_probabilities"], f"{where}.pick_probabilities")
    out: dict[str, Fraction] = {}
    for move, prob in picks.items():
        move = _move(move, f"{where}.pick_probabilities")
        try:
            out[move] = Fraction(_str(prob, f"{where}.pick_probabilities[{move!r}]"))
        except (ValueError, ZeroDivisionError):
            raise CaseError(f"{where}.pick_probabilities[{move!r}]: {prob!r} is "
                            f"not a fraction string like '3/4'") from None
    if set(out) != set(ai_moves):
        raise CaseError(f"{where}.pick_probabilities: moves {sorted(out)} do not "
                        f"match the AI's move set {sorted(ai_moves)}")
    total = sum(out.values(), Fraction(0))
    if total != 1:
        raise CaseError(f"{where}.pick_probabilities: probabilities sum to "
                        f"{total}, not 1")
    return out


# --- entry points ------------------------------------------------------------

def load_case_dict(doc: dict, *, where: str = "<case>") -> Case:
    doc = _dict(doc, where)
    _keys(doc, where, required=("format", "name", "battle"),
          optional=("source", "notes", "damage", "expected"))
    if doc["format"] != FORMAT:
        raise CaseError(f"{where}.format: expected {FORMAT}, got {doc['format']!r}")

    battle_obj = _dict(doc["battle"], f"{where}.battle")
    _keys(battle_obj, f"{where}.battle", required=("flags", "ai", "player"),
          optional=("field", "doubles", "frontier"))
    if _bool(battle_obj.get("doubles", False), f"{where}.battle.doubles"):
        raise CaseError(f"{where}.battle.doubles: doubles battles are not "
                        f"supported yet")

    battle = Battle(
        ai=_side(battle_obj["ai"], f"{where}.battle.ai", moves_required=True),
        player=_side(battle_obj["player"], f"{where}.battle.player",
                     moves_required=False),
        field=_field(battle_obj.get("field", {}), f"{where}.battle.field"),
        flags=_flags(battle_obj["flags"], f"{where}.battle.flags"),
        frontier=_bool(battle_obj.get("frontier", False),
                       f"{where}.battle.frontier"),
    )

    if "damage" in doc:
        damage = _damage(doc["damage"], f"{where}.damage",
                         battle.ai.active.moves)
    else:
        damage = CalcBackend()

    expected = None
    if "expected" in doc:
        expected = _expected(doc["expected"], f"{where}.expected",
                             battle.ai.active.moves)

    notes = doc.get("notes", [])
    if isinstance(notes, str):
        notes = (notes,)
    elif isinstance(notes, list):
        notes = tuple(_str(n, f"{where}.notes[{i}]") for i, n in enumerate(notes))
    else:
        raise CaseError(f"{where}.notes: expected a string or list of strings")

    source = doc.get("source")
    return Case(
        name=_str(doc["name"], f"{where}.name"),
        battle=battle,
        damage=damage,
        source=None if source is None else _str(source, f"{where}.source"),
        notes=notes,
        expected=expected,
    )


def load_case(path: str | Path) -> Case:
    path = Path(path)
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise CaseError(f"{path}: invalid JSON: {exc}") from None
    case = load_case_dict(doc, where=path.name)
    case.path = path
    return case
