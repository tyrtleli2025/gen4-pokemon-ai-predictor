"""Held-item data, backed by data/items.csv (all 446 items, generated from
the decomp's per-item JSON by tools/gen_items.py; Kaizo's Item Changes tab
was empty at export, so vanilla item data stands).

`hold_effect` translates the decomp's HOLD_EFFECT_* constants into the small
set of effect ids the damage formula consumes. An item whose hold effect is
not damage-relevant (Focus Sash, Leftovers, ...) is a *correct* no-op --
(None, 0) -- while an unrecognised item NAME is a loading error upstream
(case_loader validates names against this table).

Two effect families live OUTSIDE BattleSystem_CalcMoveDamage, in the battle
script layer, so they only apply to battle-order damage (battle_order.py) and
never to the AI's own damage view: Life Orb (HOLD_EFFECT_HP_DRAIN_ON_ATK,
+30% in BtlCmd_CalcDamage before the variance) and the type-resist berries
(HOLD_EFFECT_WEAKEN_*, subscript_type_resist_berry halves the final damage).
TrainerAI_CalcDamage contains neither -- verified by grep -- so the AI
genuinely mis-estimates damage around them.
"""
from __future__ import annotations

import csv
import difflib
from functools import lru_cache
from pathlib import Path

from ..names import UnknownName, squash

_DATA = Path(__file__).resolve().parent.parent.parent / "data"

_TYPE_BOOSTS = {
    f"HOLD_EFFECT_STRENGTHEN_{suffix}": type_name
    for suffix, type_name in (
        ("NORMAL", "Normal"), ("FIGHT", "Fighting"), ("FLYING", "Flying"),
        ("POISON", "Poison"), ("GROUND", "Ground"), ("ROCK", "Rock"),
        ("BUG", "Bug"), ("GHOST", "Ghost"), ("STEEL", "Steel"),
        ("FIRE", "Fire"), ("WATER", "Water"), ("GRASS", "Grass"),
        ("ELECTRIC", "Electric"), ("PSYCHIC", "Psychic"), ("ICE", "Ice"),
        ("DRAGON", "Dragon"), ("DARK", "Dark"),
    )
}

_PLATES = {
    f"HOLD_EFFECT_ARCEUS_{suffix}": type_name
    for suffix, type_name in (
        ("FIRE", "Fire"), ("WATER", "Water"), ("ELECTRIC", "Electric"),
        ("GRASS", "Grass"), ("ICE", "Ice"), ("FIGHTING", "Fighting"),
        ("POISON", "Poison"), ("GROUND", "Ground"), ("FLYING", "Flying"),
        ("PSYCHIC", "Psychic"), ("BUG", "Bug"), ("ROCK", "Rock"),
        ("GHOST", "Ghost"), ("DRAGON", "Dragon"), ("DARK", "Dark"),
        ("STEEL", "Steel"),
    )
}

#: HOLD_EFFECT_* -> the effect id the damage formula consumes.
_SIMPLE_EFFECTS = {
    "HOLD_EFFECT_POWER_UP_PHYS": "muscle_band",
    "HOLD_EFFECT_POWER_UP_SPEC": "wise_glasses",
    "HOLD_EFFECT_POWER_UP_SE": "expert_belt",
    "HOLD_EFFECT_CHOICE_ATK": "choice_atk",
    "HOLD_EFFECT_CHOICE_SPATK": "choice_spatk",
    "HOLD_EFFECT_SPEED_DOWN_GROUNDED": "iron_ball",
    "HOLD_EFFECT_PIKA_SPATK_UP": "light_ball",
    "HOLD_EFFECT_CUBONE_ATK_UP": "thick_club",
    "HOLD_EFFECT_DITTO_DEF_UP": "metal_powder",
    "HOLD_EFFECT_CLAMPERL_SPATK": "deep_sea_tooth",
    "HOLD_EFFECT_CLAMPERL_SPDEF": "deep_sea_scale",
    "HOLD_EFFECT_LATI_SPECIAL": "soul_dew",
    "HOLD_EFFECT_DIALGA_BOOST": "adamant_orb",
    "HOLD_EFFECT_PALKIA_BOOST": "lustrous_orb",
    "HOLD_EFFECT_GIRATINA_BOOST": "griseous_orb",
    "HOLD_EFFECT_HP_DRAIN_ON_ATK": "life_orb",
}

#: HOLD_EFFECT_WEAKEN_SE_* -> the attacking type the berry halves.
_WEAKEN_BERRIES = {
    f"HOLD_EFFECT_WEAKEN_SE_{suffix}": type_name
    for suffix, type_name in (
        ("FIRE", "Fire"), ("WATER", "Water"), ("ELECTRIC", "Electric"),
        ("GRASS", "Grass"), ("ICE", "Ice"), ("FIGHT", "Fighting"),
        ("POISON", "Poison"), ("GROUND", "Ground"), ("FLYING", "Flying"),
        ("PSYCHIC", "Psychic"), ("BUG", "Bug"), ("ROCK", "Rock"),
        ("GHOST", "Ghost"), ("DRAGON", "Dragon"), ("DARK", "Dark"),
        ("STEEL", "Steel"),
    )
}


@lru_cache(maxsize=1)
def _table() -> dict[str, dict]:
    """squash(name) -> row, for every item in the game."""
    rows: dict[str, dict] = {}
    with (_DATA / "items.csv").open() as fh:
        for row in csv.DictReader(fh):
            rows[squash(row["Name"])] = row
    return rows


def canonical_item(name: str) -> str:
    """The game's spelling for an item name; raises UnknownName with a
    suggestion for typos."""
    row = _table().get(squash(name))
    if row is not None:
        return row["Name"]
    close = difflib.get_close_matches(
        name, [r["Name"] for r in _table().values()], n=1)
    hint = f"; did you mean {close[0]!r}?" if close else ""
    raise UnknownName(f"unknown item {name!r}{hint}")


def known_item(name: str) -> bool:
    return squash(name) in _table()


def all_items() -> list[str]:
    """Every canonical item name, sorted (for UI dropdowns)."""
    return sorted(row["Name"] for row in _table().values())


def hold_effect(item: str | None) -> tuple[str | None, int]:
    """(damage-relevant effect id, effect power). (None, 0) when the item is
    None or its hold effect does not touch the damage formula."""
    if item is None:
        return (None, 0)
    row = _table().get(squash(item))
    if row is None:
        return (None, 0)
    effect = row["Hold Effect"]
    param = int(row["Effect Param"])
    if effect in _TYPE_BOOSTS:
        return (f"boost_{_TYPE_BOOSTS[effect]}", param)
    if effect in _PLATES:
        return (f"boost_{_PLATES[effect]}", param)
    if effect in _SIMPLE_EFFECTS:
        return (_SIMPLE_EFFECTS[effect], param)
    return (None, 0)


def weaken_berry(item: str | None) -> tuple[str, bool] | None:
    """(attacking type the berry halves, requires_super_effective), or None.

    subscript_type_resist_berry: the typed berries (Occa...Babiri) halve the
    final damage of a super-effective hit of their type; Chilan halves any
    Normal hit, checked before the super-effective gate."""
    if item is None:
        return None
    row = _table().get(squash(item))
    if row is None:
        return None
    effect = row["Hold Effect"]
    if effect == "HOLD_EFFECT_WEAKEN_NORMAL":
        return ("Normal", False)
    wtype = _WEAKEN_BERRIES.get(effect)
    return (wtype, True) if wtype else None


def plate_type(item: str | None) -> str | None:
    """The Arceus-plate type an item grants Judgment, or None."""
    if item is None:
        return None
    row = _table().get(squash(item))
    if row is None:
        return None
    return _PLATES.get(row["Hold Effect"])


def natural_gift(item: str | None) -> tuple[int, str | None]:
    """(power, type) Natural Gift gets from the held item; (0, None) if the
    item grants none (non-berries have power 0 in the data)."""
    if item is None:
        return (0, None)
    row = _table().get(squash(item))
    if row is None:
        return (0, None)
    power = int(row["Natural Gift Power"])
    return (power, row["Natural Gift Type"] or None) if power else (0, None)
