"""The simulator's API surface: pure dict-in/dict-out functions.

No HTTP objects anywhere -- aicalc/serve/http.py maps these onto routes, and
tests call them directly. All engine errors propagate; the HTTP layer owns
turning them into status codes.
"""
from __future__ import annotations

import csv
from dataclasses import asdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from .. import movedata
from ..case_loader import (BOOST_KEYS, GENDERS, HAZARDS, STATUSES, TYPES,
                           WEATHERS, load_case_dict)
from ..flags._blocks import all_moves
from ..names import _FLAG_DISPLAY
from ..predicates import Context
from ..scoring import (FLAG_MODULES, action_score_distributions, active_flags,
                       flag_distribution)
from ..select import action_probabilities
from ..state import VOLATILES, legal_actions
from ..stats import NATURE_ORDER, NATURES
from ..trainers import (build_pokemon, decode_ai_flags, load_trainer,
                        species_names, species_row, trainer_index)

_DATA = Path(__file__).resolve().parent.parent.parent / "data"


def meta() -> dict:
    return {
        "flags": {"supported": sorted(FLAG_MODULES),
                  "display": list(_FLAG_DISPLAY)},
        "statuses": sorted(STATUSES),
        "weathers": sorted(WEATHERS),
        "hazards": sorted(HAZARDS),
        "types": sorted(TYPES),
        "volatiles": sorted(VOLATILES),
        "genders": sorted(GENDERS),
        "boost_keys": sorted(BOOST_KEYS),
        "natures": list(NATURE_ORDER),
        "nature_effects": {name: list(NATURES[name]) for name in NATURE_ORDER},
    }


def trainers() -> dict:
    return {"trainers": trainer_index()}


def trainer(tr_id: int) -> dict:
    data = load_trainer(tr_id)
    party = []
    for entry in data["party"]:
        mon = build_pokemon(entry)
        supported, unsupported = decode_ai_flags(entry["ai_mask"])
        doc = asdict(mon)
        doc["types"] = list(doc["types"])
        doc["volatiles"] = sorted(doc["volatiles"])
        doc["moves_used"] = sorted(doc["moves_used"])
        party.append({
            "pokemon": doc,
            "nature": entry["nature"],
            "ivs": entry["ivs"],
            "ai_flags": sorted(supported),
            "unsupported_flags": sorted(unsupported),
        })
    return {"id": data["id"], "name": data["name"],
            "location": data["location"], "battle_type": data["battle_type"],
            "party": party}


@lru_cache(maxsize=1)
def _move_effects() -> dict[str, dict]:
    rows = {}
    with (_DATA / "move_effects.csv").open() as fh:
        for row in csv.DictReader(fh):
            rows[row["Name"]] = {"effect": row["Effect"],
                                 "chance": int(row["Chance"] or 0)}
    return rows


def tables() -> dict:
    moves = {}
    for name in sorted(all_moves()):
        if not movedata.known(name):
            continue
        effect = _move_effects().get(name, {})
        moves[name] = {
            "type": movedata.move_type(name),
            "category": movedata.category(name),
            "power": movedata.power(name),
            "pp": movedata.base_pp(name),
            "priority": movedata.priority(name),
            "effect": effect.get("effect"),
            "effect_chance": effect.get("chance", 0),
        }
    species = {}
    for name in species_names():
        row = species_row(name)
        species[name] = {
            "base": {"hp": int(row["HP"]), "atk": int(row["Atk"]),
                     "def": int(row["Def"]), "spa": int(row["SpA"]),
                     "spd": int(row["SpD"]), "spe": int(row["Spe"])},
            "types": [t for t in (row["Type1"], row["Type2"]) if t],
            "abilities": [a for a in (row["Ability1"], row["Ability2"]) if a],
            "weight_hg": int(row["WeightHg"]),
        }
    from ..calc.items import all_items
    return {"moves": moves, "species": species, "items": all_items()}


def _dist_pairs(dist) -> list[list]:
    return [[score, str(prob)] for score, prob in dist.table.items()]


def _load_live(doc: dict):
    if "battle" not in doc:
        doc = {"format": 1, "name": "live", "battle": doc}
    doc.setdefault("format", 1)
    doc.setdefault("name", "live")
    return load_case_dict(doc, where="<live>")


def probabilities(doc: dict) -> dict:
    case = _load_live(doc)
    battle, damage = case.battle, case.damage

    flags = active_flags(battle)
    dists = action_score_distributions(battle, damage)
    picks = action_probabilities(dists)

    actions = []
    for action in legal_actions(battle):
        ctx = Context(battle=battle, action=action, damage=damage)
        flag_dists = {}
        for flag in flags:
            dist = flag_distribution(flag, ctx)
            if dist.table != {0: Fraction(1)}:
                flag_dists[flag] = _dist_pairs(dist)
        pick = picks[action]
        actions.append({
            "move": action.move,
            "flag_dists": flag_dists,
            "final_dist": _dist_pairs(dists[action]),
            "pick": {"fraction": str(pick), "float": float(pick)},
        })
    actions.sort(key=lambda a: -float(a["pick"]["float"]))
    return {"active_flags": flags, "actions": actions}


#: Effects whose real battle damage cannot come out of the roll formula at
#: all (incoming-damage reflectors, OHKO, HP-equalisers, item/party-driven
#: power). Shown as n/a rather than a wrong number.
_UNMODELLED_EFFECTS = frozenset({
    "BATTLE_EFFECT_COUNTER", "BATTLE_EFFECT_MIRROR_COAT",
    "BATTLE_EFFECT_ONE_HIT_KO", "BATTLE_EFFECT_AVERAGE_HP",
    "BATTLE_EFFECT_HALVE_HP", "BATTLE_EFFECT_SET_HP_EQUAL_TO_USER",
    "BATTLE_EFFECT_BEAT_UP", "BATTLE_EFFECT_FLING",
    "BATTLE_EFFECT_RANDOM_POWER_MAYBE_HEAL",
})

#: Effects with a conditional/scaling power modifier the roll display does
#: not apply; the flat-data-power number is shown with this caveat.
_POWER_CAVEATS = {
    "BATTLE_EFFECT_DOUBLE_POWER_WHEN_BELOW_HALF":
        "power doubles below half HP (not applied)",
    "BATTLE_EFFECT_DOUBLE_POWER_IF_MOVING_SECOND":
        "power doubles when moving second (not applied)",
    "BATTLE_EFFECT_DOUBLE_POWER_AND_CURE_PARALYSIS":
        "power doubles vs paralysis (not applied)",
    "BATTLE_EFFECT_DOUBLE_DAMAGE_DIG": "double damage vs Dig (not applied)",
    "BATTLE_EFFECT_DOUBLE_DAMAGE_DIVE": "double damage vs Dive (not applied)",
    "BATTLE_EFFECT_DOUBLE_DAMAGE_FLY_OR_BOUNCE":
        "double damage vs Fly/Bounce (not applied)",
    "BATTLE_EFFECT_INCREASE_POWER_WITH_LESS_HP":
        "power scales with the user's missing HP; shown at data power",
    "BATTLE_EFFECT_DECREASE_POWER_WITH_LESS_USER_HP":
        "power scales down with the user's missing HP; shown at full power",
    "BATTLE_EFFECT_HIGHER_POWER_WHEN_LOW_PP":
        "power rises at low PP; shown at data power",
    "BATTLE_EFFECT_INCREASE_POWER_WITH_MORE_STAT_UP":
        "power scales with stat boosts; shown at data power",
    "BATTLE_EFFECT_HIT_TWICE": "per-hit damage (hits twice)",
    "BATTLE_EFFECT_HIT_THREE_TIMES": "per-hit damage (hits three times)",
}


def _trunc_pct(value: int, max_hp: int) -> float:
    """Percent of max HP truncated to one decimal (HZLA's display rule)."""
    return (value * 1000 // max_hp) / 10


def _ko_text(outcomes, defender) -> str:
    hp = defender.current_hp
    p_ohko = sum((prob * Fraction(sum(1 for r in rolls if r >= hp), 16)
                  for prob, _, rolls in outcomes), Fraction(0))
    if p_ohko == 1:
        return "guaranteed OHKO"
    if p_ohko > 0:
        return f"{float(p_ohko) * 100:.1f}% chance to OHKO"
    lo = min(min(rolls) for _, _, rolls in outcomes)
    hi = max(max(rolls) for _, _, rolls in outcomes)
    if hi == 0:
        return "no damage"
    n_best = -(-hp // hi)   # ceil: fewest hits at max rolls
    n_sure = -(-hp // lo) if lo else None
    if n_sure is None:
        return f"{n_best}HKO best case"
    if n_best == n_sure:
        return f"guaranteed {n_sure}HKO"
    return f"{n_best}HKO best case, guaranteed {n_sure}HKO"


def _damage_entry(battle, move, attacker, atk_side, defender, def_side) -> dict:
    from ..calc.ai_damage import NeedsManualFact
    from ..calc.battle_order import battle_damage_outcomes

    effect = _move_effects().get(move, {}).get("effect")
    entry = {"move": move, "type": movedata.move_type(move),
             "category": movedata.category(move)}
    if entry["category"] == "Status":
        entry["kind"] = "status"
        return entry
    if effect in _UNMODELLED_EFFECTS:
        entry["kind"] = "unmodelled"
        entry["reason"] = (f"{move}: {effect.removeprefix('BATTLE_EFFECT_')} "
                           f"damage depends on state the roll calc does not "
                           f"model")
        return entry
    try:
        outcomes = battle_damage_outcomes(battle, move, attacker, atk_side,
                                          defender, def_side)
    except (NeedsManualFact, NotImplementedError) as exc:
        entry["kind"] = "unmodelled"
        entry["reason"] = str(exc)
        return entry

    max_hp = defender.max_hp
    entry["kind"] = "damage"
    entry["outcomes"] = [{
        "chance": str(prob), "desc": desc, "rolls": rolls,
        "min": min(rolls), "max": max(rolls),
        "min_pct": _trunc_pct(min(rolls), max_hp),
        "max_pct": _trunc_pct(max(rolls), max_hp),
    } for prob, desc, rolls in outcomes]
    entry["min"] = min(o["min"] for o in entry["outcomes"])
    entry["max"] = max(o["max"] for o in entry["outcomes"])
    entry["min_pct"] = _trunc_pct(entry["min"], max_hp)
    entry["max_pct"] = _trunc_pct(entry["max"], max_hp)
    entry["ko"] = _ko_text(outcomes, defender)
    caveat = _POWER_CAVEATS.get(effect)
    if caveat:
        entry["caveat"] = caveat
    return entry


def damage(doc: dict) -> dict:
    """Battle-order damage rolls for every move on both sides."""
    battle = _load_live(doc).battle
    return {
        "player": [_damage_entry(battle, m, battle.player.active,
                                 battle.player, battle.ai.active, battle.ai)
                   for m in battle.player.active.moves],
        "ai": [_damage_entry(battle, m, battle.ai.active, battle.ai,
                             battle.player.active, battle.player)
               for m in battle.ai.active.moves],
    }
