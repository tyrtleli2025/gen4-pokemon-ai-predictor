"""Gen 4 type chart application, ported from BattleSystem_ApplyTypeChart
(battle_lib.c:2560-2679) and ApplyTypeMultiplier (battle_lib.c:7542).

The chart itself is sTypeMatchupMultipliers (battle_lib.c:2399) transcribed
verbatim, including the 0xFE separator before the two Ghost immunities that
Foresight/Scrappy bypass, and the multiplier encoding (0 immune, 5 not very
effective, 20 super effective; applied as damage*mul/10 via game_divide).
"""
from __future__ import annotations

from .. import movedata
from ..state import Battle, Pokemon, Side
from .divmath import c_div, game_divide
from .items import hold_effect

# MOVE_STATUS_* flags (include/constants/battle/moves.h)
SUPER_EFFECTIVE = 1 << 1
NOT_VERY_EFFECTIVE = 1 << 2
INEFFECTIVE = 1 << 3
LEVITATED = 1 << 11
WONDER_GUARD = 1 << 18
MAGNET_RISE = 1 << 20
IMMUNE = INEFFECTIVE | WONDER_GUARD | LEVITATED | MAGNET_RISE

_IMM, _NVE, _SE = 0, 5, 20

#: The separator row: the entries after it are the Ghost immunities that
#: Foresight (on the defender) or Scrappy (on the attacker) bypass.
_FORESIGHT_BREAK = ("<foresight>", "<foresight>", _IMM)

CHART: tuple[tuple[str, str, int], ...] = (
    ("Normal", "Rock", _NVE), ("Normal", "Steel", _NVE),
    ("Fire", "Fire", _NVE), ("Fire", "Water", _NVE), ("Fire", "Grass", _SE),
    ("Fire", "Ice", _SE), ("Fire", "Bug", _SE), ("Fire", "Rock", _NVE),
    ("Fire", "Dragon", _NVE), ("Fire", "Steel", _SE),
    ("Water", "Fire", _SE), ("Water", "Water", _NVE), ("Water", "Grass", _NVE),
    ("Water", "Ground", _SE), ("Water", "Rock", _SE), ("Water", "Dragon", _NVE),
    ("Electric", "Water", _SE), ("Electric", "Electric", _NVE),
    ("Electric", "Grass", _NVE), ("Electric", "Ground", _IMM),
    ("Electric", "Flying", _SE), ("Electric", "Dragon", _NVE),
    ("Grass", "Fire", _NVE), ("Grass", "Water", _SE), ("Grass", "Grass", _NVE),
    ("Grass", "Poison", _NVE), ("Grass", "Ground", _SE), ("Grass", "Flying", _NVE),
    ("Grass", "Bug", _NVE), ("Grass", "Rock", _SE), ("Grass", "Dragon", _NVE),
    ("Grass", "Steel", _NVE),
    ("Ice", "Water", _NVE), ("Ice", "Grass", _SE), ("Ice", "Ice", _NVE),
    ("Ice", "Ground", _SE), ("Ice", "Flying", _SE), ("Ice", "Dragon", _SE),
    ("Ice", "Steel", _NVE), ("Ice", "Fire", _NVE),
    ("Fighting", "Normal", _SE), ("Fighting", "Ice", _SE),
    ("Fighting", "Poison", _NVE), ("Fighting", "Flying", _NVE),
    ("Fighting", "Psychic", _NVE), ("Fighting", "Bug", _NVE),
    ("Fighting", "Rock", _SE), ("Fighting", "Dark", _SE),
    ("Fighting", "Steel", _SE),
    ("Poison", "Grass", _SE), ("Poison", "Poison", _NVE),
    ("Poison", "Ground", _NVE), ("Poison", "Rock", _NVE),
    ("Poison", "Ghost", _NVE), ("Poison", "Steel", _IMM),
    ("Ground", "Fire", _SE), ("Ground", "Electric", _SE),
    ("Ground", "Grass", _NVE), ("Ground", "Poison", _SE),
    ("Ground", "Flying", _IMM), ("Ground", "Bug", _NVE),
    ("Ground", "Rock", _SE), ("Ground", "Steel", _SE),
    ("Flying", "Electric", _NVE), ("Flying", "Grass", _SE),
    ("Flying", "Fighting", _SE), ("Flying", "Bug", _SE),
    ("Flying", "Rock", _NVE), ("Flying", "Steel", _NVE),
    ("Psychic", "Fighting", _SE), ("Psychic", "Poison", _SE),
    ("Psychic", "Psychic", _NVE), ("Psychic", "Dark", _IMM),
    ("Psychic", "Steel", _NVE),
    ("Bug", "Fire", _NVE), ("Bug", "Grass", _SE), ("Bug", "Fighting", _NVE),
    ("Bug", "Poison", _NVE), ("Bug", "Flying", _NVE), ("Bug", "Psychic", _SE),
    ("Bug", "Ghost", _NVE), ("Bug", "Dark", _SE), ("Bug", "Steel", _NVE),
    ("Rock", "Fire", _SE), ("Rock", "Ice", _SE), ("Rock", "Fighting", _NVE),
    ("Rock", "Ground", _NVE), ("Rock", "Flying", _SE), ("Rock", "Bug", _SE),
    ("Rock", "Steel", _NVE),
    ("Ghost", "Normal", _IMM), ("Ghost", "Psychic", _SE),
    ("Ghost", "Dark", _NVE), ("Ghost", "Steel", _NVE), ("Ghost", "Ghost", _SE),
    ("Dragon", "Dragon", _SE), ("Dragon", "Steel", _NVE),
    ("Dark", "Fighting", _NVE), ("Dark", "Psychic", _SE), ("Dark", "Ghost", _SE),
    ("Dark", "Dark", _NVE), ("Dark", "Steel", _NVE),
    ("Steel", "Fire", _NVE), ("Steel", "Water", _NVE),
    ("Steel", "Electric", _NVE), ("Steel", "Ice", _SE), ("Steel", "Rock", _SE),
    ("Steel", "Steel", _NVE),
    _FORESIGHT_BREAK,
    ("Normal", "Ghost", _IMM), ("Fighting", "Ghost", _IMM),
)


def _defender_types(defender: Pokemon) -> tuple[str, str]:
    type1 = defender.types[0]
    type2 = defender.types[1] if len(defender.types) > 1 else type1
    return type1, type2


def _ignorable_ability(attacker: Pokemon, defender: Pokemon, ability: str) -> bool:
    """Battler_IgnorableAbility: defender has it and attacker lacks Mold Breaker."""
    return attacker.ability != "Mold Breaker" and defender.ability == ability


def _apply_multiplier(mul: int, damage: int, update: bool, flags: int,
                      ignore_type_checks: bool) -> tuple[int, int]:
    """ApplyTypeMultiplier (battle_lib.c:7542)."""
    if not ignore_type_checks and damage:
        damage = game_divide(damage * mul, 10)

    if mul == _IMM:
        flags |= INEFFECTIVE
        flags &= ~NOT_VERY_EFFECTIVE
        flags &= ~SUPER_EFFECTIVE
    elif mul == _NVE:
        if update:
            if flags & SUPER_EFFECTIVE:
                flags &= ~SUPER_EFFECTIVE
            else:
                flags |= NOT_VERY_EFFECTIVE
    elif mul == _SE:
        if update:
            if flags & NOT_VERY_EFFECTIVE:
                flags &= ~NOT_VERY_EFFECTIVE
            else:
                flags |= SUPER_EFFECTIVE
    return damage, flags


def _basic_mul_applies(battle: Battle, defender: Pokemon,
                       row: tuple[str, str, int]) -> bool:
    """BasicTypeMulApplies: effects that suspend a chart row."""
    _, def_type, mul = row
    grounded_item = hold_effect(defender.item)[0] == "iron_ball"
    if ((grounded_item or "ingrain" in defender.volatiles)
            and def_type == "Flying" and mul == _IMM):
        return False
    # Roost is un-modelled state; if it ever matters, model it loudly rather
    # than silently skipping Flying rows.
    if battle.field.gravity and def_type == "Flying" and mul == _IMM:
        return False
    if ("miracle_eye" in defender.volatiles
            and def_type == "Dark" and mul == _IMM):
        return False
    return True


def apply_type_chart(battle: Battle, move: str, attacker: Pokemon,
                     defender: Pokemon, damage: int, *,
                     move_type: str | None = None,
                     ignore_type_checks: bool = False) -> tuple[int, int]:
    """BattleSystem_ApplyTypeChart. Returns (damage, MOVE_STATUS flags)."""
    flags = 0

    if attacker.ability == "Normalize":
        mtype = "Normal"
    elif move_type is not None:
        mtype = move_type
    else:
        mtype = movedata.move_type(move)

    move_power = movedata.power(move)

    # STAB (Adaptability doubles instead).
    if not ignore_type_checks and mtype in attacker.types:
        if attacker.ability == "Adaptability":
            damage *= 2
        else:
            damage = c_div(damage * 15, 10)

    defender_grounding_item = hold_effect(defender.item)[0] == "iron_ball"
    if (_ignorable_ability(attacker, defender, "Levitate")
            and mtype == "Ground" and not defender_grounding_item):
        flags |= LEVITATED
    elif ("magnet_rise" in defender.volatiles
            and "ingrain" not in defender.volatiles
            and mtype == "Ground" and not defender_grounding_item):
        flags |= MAGNET_RISE
    else:
        type1, type2 = _defender_types(defender)
        past_break = False
        for row in CHART:
            if row is _FORESIGHT_BREAK:
                # Ghost immunities are bypassed by Foresight or Scrappy.
                if ("foresight" in defender.volatiles
                        or attacker.ability == "Scrappy"):
                    break
                past_break = True
                continue
            if past_break:
                pass  # the trailing immunities are evaluated like normal rows
            atk_type, def_type, mul = row
            if atk_type != mtype:
                continue
            if def_type == type1 and _basic_mul_applies(battle, defender, row):
                damage, flags = _apply_multiplier(mul, damage, bool(move_power),
                                                  flags, ignore_type_checks)
            if (def_type == type2 and type1 != type2
                    and _basic_mul_applies(battle, defender, row)):
                damage, flags = _apply_multiplier(mul, damage, bool(move_power),
                                                  flags, ignore_type_checks)

    if (_ignorable_ability(attacker, defender, "Wonder Guard")
            and (not (flags & SUPER_EFFECTIVE)
                 or (flags & (SUPER_EFFECTIVE | NOT_VERY_EFFECTIVE))
                 == (SUPER_EFFECTIVE | NOT_VERY_EFFECTIVE))
            and move_power):
        flags |= WONDER_GUARD
    elif not ignore_type_checks:
        if (flags & SUPER_EFFECTIVE) and move_power:
            if (_ignorable_ability(attacker, defender, "Filter")
                    or _ignorable_ability(attacker, defender, "Solid Rock")):
                damage = game_divide(damage * 3, 4)
            effect, item_power = hold_effect(attacker.item)
            if effect == "expert_belt":
                damage = c_div(damage * (100 + item_power), 100)
        if (flags & NOT_VERY_EFFECTIVE) and move_power:
            if attacker.ability == "Tinted Lens":
                damage *= 2
    else:
        flags &= ~SUPER_EFFECTIVE
        flags &= ~NOT_VERY_EFFECTIVE

    return damage, flags


def effectiveness_bucket(battle: Battle, move: str, attacker: Pokemon,
                         defender: Pokemon) -> float:
    """AICmd_IfMoveEffectivenessEquals (trainer_ai.c:1312): the multiplier the
    AI's effectiveness checks see. Starts from damage 40, applies the chart
    (STAB included), remaps the STAB-composed values, zeroes on any immunity
    flag, and divides by 40.

    Values off the exact buckets (plain STAB 60, Filter-distorted 80->60...)
    return non-bucket multipliers like 1.5, which -- exactly like the real AI
    -- match no block's equality check.
    """
    damage, flags = apply_type_chart(battle, move, attacker, defender, 40)
    remap = {120: 80, 240: 160, 30: 20, 15: 10}
    damage = remap.get(damage, damage)
    if flags & IMMUNE:
        damage = 0
    return damage / 40
