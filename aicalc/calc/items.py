"""Damage-relevant held-item effects, keyed by squashed item name.

Covers the items the Gen 4 damage formula reads (battle_lib.c's
sTypeBoostingItems plus the stat/power hold effects). An unknown or
irrelevant item is a documented no-op -- the formula only ever asks "does
this item have effect X", so Lum Berry, Focus Sash etc. simply never match.
Life Orb is deliberately absent: its boost is applied outside
BattleSystem_CalcMoveDamage and is invisible to the AI's damage calc.
"""
from __future__ import annotations

from functools import lru_cache

from ..names import squash

#: name -> (effect, power). Type-boost items are 20% in Gen 4.
_ITEMS: dict[str, tuple[str, int]] = {
    # Type boosters (sTypeBoostingItems); plates and incenses included.
    "Silk Scarf": ("boost_Normal", 20),
    "Charcoal": ("boost_Fire", 20), "Flame Plate": ("boost_Fire", 20),
    "Mystic Water": ("boost_Water", 20), "Splash Plate": ("boost_Water", 20),
    "Sea Incense": ("boost_Water", 20), "Wave Incense": ("boost_Water", 20),
    "Miracle Seed": ("boost_Grass", 20), "Meadow Plate": ("boost_Grass", 20),
    "Rose Incense": ("boost_Grass", 20),
    "Magnet": ("boost_Electric", 20), "Zap Plate": ("boost_Electric", 20),
    "NeverMeltIce": ("boost_Ice", 20), "Icicle Plate": ("boost_Ice", 20),
    "Black Belt": ("boost_Fighting", 20), "Fist Plate": ("boost_Fighting", 20),
    "Poison Barb": ("boost_Poison", 20), "Toxic Plate": ("boost_Poison", 20),
    "Soft Sand": ("boost_Ground", 20), "Earth Plate": ("boost_Ground", 20),
    "Sharp Beak": ("boost_Flying", 20), "Sky Plate": ("boost_Flying", 20),
    "TwistedSpoon": ("boost_Psychic", 20), "Mind Plate": ("boost_Psychic", 20),
    "Odd Incense": ("boost_Psychic", 20),
    "SilverPowder": ("boost_Bug", 20), "Insect Plate": ("boost_Bug", 20),
    "Hard Stone": ("boost_Rock", 20), "Stone Plate": ("boost_Rock", 20),
    "Rock Incense": ("boost_Rock", 20),
    "Spell Tag": ("boost_Ghost", 20), "Spooky Plate": ("boost_Ghost", 20),
    "Dragon Fang": ("boost_Dragon", 20), "Draco Plate": ("boost_Dragon", 20),
    "BlackGlasses": ("boost_Dark", 20), "Dread Plate": ("boost_Dark", 20),
    "Metal Coat": ("boost_Steel", 20), "Iron Plate": ("boost_Steel", 20),

    # Class/stat boosters.
    "Muscle Band": ("muscle_band", 10),
    "Wise Glasses": ("wise_glasses", 10),
    "Choice Band": ("choice_atk", 0),
    "Choice Specs": ("choice_spatk", 0),
    "Expert Belt": ("expert_belt", 20),

    # Grounding (HOLD_EFFECT_SPEED_DOWN_GROUNDED).
    "Iron Ball": ("iron_ball", 0),

    # Species items.
    "Light Ball": ("light_ball", 0),
    "Thick Club": ("thick_club", 0),
    "Metal Powder": ("metal_powder", 0),
    "DeepSeaTooth": ("deep_sea_tooth", 0),
    "DeepSeaScale": ("deep_sea_scale", 0),
    "Soul Dew": ("soul_dew", 0),
    "Adamant Orb": ("adamant_orb", 20),
    "Lustrous Orb": ("lustrous_orb", 20),
    "Griseous Orb": ("griseous_orb", 20),
}


@lru_cache(maxsize=1)
def _by_squash() -> dict[str, tuple[str, int]]:
    return {squash(name): entry for name, entry in _ITEMS.items()}


def hold_effect(item: str | None) -> tuple[str | None, int]:
    """(effect id, effect power) for a held item; (None, 0) if none/unknown."""
    if item is None:
        return (None, 0)
    return _by_squash().get(squash(item), (None, 0))
