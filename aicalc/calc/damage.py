"""The Gen 4 damage formula: BattleSystem_CalcMoveDamage
(battle_lib.c:6601-7079), ported statement-for-statement in C order.

Always called with criticalMul == 1 here (the AI never assumes crits), so the
crit-conditional stage clamps collapse to the plain stage multipliers.
Branches that Kaizo singles cannot reach raise loudly instead of silently
mis-modelling: doubles screen/spread math, Helping Hand, Slow Start.
"""
from __future__ import annotations

from .. import movedata
from ..state import Battle, Pokemon, Side
from .divmath import c_div
from .items import hold_effect

#: sStatStageBoosts (battle_lib.c): (numerator, denominator) for stages -6..+6.
STAGE_BOOSTS = (
    (10, 40), (10, 35), (10, 30), (10, 25), (10, 20), (10, 15),
    (10, 10),
    (15, 10), (20, 10), (25, 10), (30, 10), (35, 10), (40, 10),
)

#: Kaizo's BATTLE_EFFECT_HALVE_DEFENSE moves (defender's Defense halved in the
#: formula). Verified against the scraped Basic block 31b6163f -- the trio
#: sharing the Damp check.
HALVE_DEFENSE_MOVES = frozenset({"Selfdestruct", "Explosion", "Memento"})

#: BATTLE_EFFECT_REMOVE_SCREENS: bypasses Reflect/Light Screen in the formula.
REMOVE_SCREENS_MOVES = frozenset({"Brick Break"})

#: sPunchingMoves for Iron Fist, canonical Kaizo spellings.
PUNCHING_MOVES = frozenset({
    "Ice Punch", "Fire Punch", "ThunderPunch", "Mach Punch", "Focus Punch",
    "Dizzy Punch", "DynamicPunch", "Hammer Arm", "Mega Punch", "Meteor Mash",
    "Shadow Punch", "Drain Punch", "Bullet Punch", "Sky Uppercut",
})


def _stage_apply(stat: int, stage: int) -> int:
    num, den = STAGE_BOOSTS[stage + 6]
    return c_div(stat * num, den)


def _clamp_stage(stage: int) -> int:
    return max(-6, min(6, stage))


def calc_move_damage(battle: Battle, move: str, attacker: Pokemon,
                     defender: Pokemon, attacker_side: Side,
                     defender_side: Side, *, power: int = 0,
                     move_type: str | None = None) -> int:
    """Max-roll base damage of `move`, before the type chart and variance."""
    if battle.doubles:
        raise NotImplementedError("doubles damage (screens 2/3, spread 3/4) "
                                  "is not modelled yet")

    attack_stat = attacker.stats["atk"]
    defense_stat = defender.stats["def"]
    sp_attack_stat = attacker.stats["spa"]
    sp_defense_stat = defender.stats["spd"]
    attack_stage = attacker.boosts.get("atk", 0)
    defense_stage = defender.boosts.get("def", 0)
    sp_attack_stage = attacker.boosts.get("spa", 0)
    sp_defense_stage = defender.boosts.get("spd", 0)
    level = attacker.level

    attacker_item, attacker_item_power = hold_effect(attacker.item)
    defender_item, _defender_item_power = hold_effect(defender.item)

    # Power: prefer the input power (variable-power moves), else move data.
    move_power = power if power else movedata.power(move)

    if attacker.ability == "Normalize":
        mtype = "Normal"
    elif move_type is not None:
        mtype = move_type
    else:
        mtype = movedata.move_type(move)

    # battleCtx->powerMul is 10 outside of specific scripted effects.

    if "charge" in attacker.volatiles and mtype == "Electric":
        move_power *= 2

    # turnFlags.helpingHand -- doubles-only, unreachable (guarded above).

    if attacker.ability == "Technician" and move_power <= 60:
        move_power = c_div(move_power * 15, 10)

    move_class = movedata.category(move)

    if attacker.ability in ("Huge Power", "Pure Power"):
        attack_stat *= 2
    if attacker.ability == "Slow Start":
        raise NotImplementedError("Slow Start needs a turns-since-entry "
                                  "counter that is not modelled")

    if attacker_item is not None and attacker_item == f"boost_{mtype}":
        move_power = c_div(move_power * (100 + attacker_item_power), 100)

    if attacker_item == "choice_atk":
        attack_stat = c_div(attack_stat * 150, 100)
    if attacker_item == "choice_spatk":
        sp_attack_stat = c_div(sp_attack_stat * 150, 100)
    if (attacker_item == "soul_dew" and not battle.frontier
            and attacker.species in ("Latios", "Latias")):
        sp_attack_stat = c_div(sp_attack_stat * 150, 100)
    if (defender_item == "soul_dew" and not battle.frontier
            and defender.species in ("Latios", "Latias")):
        sp_defense_stat = c_div(sp_defense_stat * 150, 100)
    if attacker_item == "deep_sea_tooth" and attacker.species == "Clamperl":
        sp_attack_stat *= 2
    if defender_item == "deep_sea_scale" and defender.species == "Clamperl":
        sp_defense_stat *= 2
    if attacker_item == "light_ball" and attacker.species == "Pikachu":
        move_power *= 2
    if defender_item == "metal_powder" and defender.species == "Ditto":
        defense_stat *= 2
    if attacker_item == "thick_club" and attacker.species in ("Cubone", "Marowak"):
        attack_stat *= 2
    if (attacker_item == "adamant_orb" and mtype in ("Dragon", "Steel")
            and attacker.species == "Dialga"):
        move_power = c_div(move_power * (100 + attacker_item_power), 100)
    if (attacker_item == "lustrous_orb" and mtype in ("Dragon", "Water")
            and attacker.species == "Palkia"):
        move_power = c_div(move_power * (100 + attacker_item_power), 100)
    if (attacker_item == "griseous_orb" and mtype in ("Dragon", "Ghost")
            and attacker.species == "Giratina"):
        move_power = c_div(move_power * (100 + attacker_item_power), 100)
    if attacker_item == "muscle_band" and move_class == "Physical":
        move_power = c_div(move_power * (100 + attacker_item_power), 100)
    if attacker_item == "wise_glasses" and move_class == "Special":
        move_power = c_div(move_power * (100 + attacker_item_power), 100)

    if _ignorable(attacker, defender, "Thick Fat") and mtype in ("Fire", "Ice"):
        move_power = c_div(move_power, 2)

    if attacker.ability == "Hustle":
        attack_stat = c_div(attack_stat * 150, 100)
    if attacker.ability == "Guts" and attacker.status is not None:
        attack_stat = c_div(attack_stat * 150, 100)
    if (_ignorable(attacker, defender, "Marvel Scale")
            and defender.status is not None):
        defense_stat = c_div(defense_stat * 150, 100)

    # Plus/Minus need a same-side partner with the twin ability -- in singles
    # the count is always zero, so no boost applies.

    actives = (battle.ai.active, battle.player.active)
    if mtype == "Electric" and any("mud_sport" in p.volatiles for p in actives):
        move_power = c_div(move_power, 2)
    if mtype == "Fire" and any("water_sport" in p.volatiles for p in actives):
        move_power = c_div(move_power, 2)

    pinch = attacker.current_hp <= c_div(attacker.max_hp, 3)
    if mtype == "Grass" and attacker.ability == "Overgrow" and pinch:
        move_power = c_div(move_power * 150, 100)
    if mtype == "Fire" and attacker.ability == "Blaze" and pinch:
        move_power = c_div(move_power * 150, 100)
    if mtype == "Water" and attacker.ability == "Torrent" and pinch:
        move_power = c_div(move_power * 150, 100)
    if mtype == "Bug" and attacker.ability == "Swarm" and pinch:
        move_power = c_div(move_power * 150, 100)

    if mtype == "Fire" and _ignorable(attacker, defender, "Heatproof"):
        move_power = c_div(move_power, 2)
    if mtype == "Fire" and _ignorable(attacker, defender, "Dry Skin"):
        move_power = c_div(move_power * 125, 100)

    if attacker.ability == "Simple":
        attack_stage = _clamp_stage(attack_stage * 2)
        sp_attack_stage = _clamp_stage(sp_attack_stage * 2)
    if _ignorable(attacker, defender, "Simple"):
        defense_stage = _clamp_stage(defense_stage * 2)
        sp_defense_stage = _clamp_stage(sp_defense_stage * 2)

    if _ignorable(attacker, defender, "Unaware"):
        attack_stage = 0
        sp_attack_stage = 0
    if attacker.ability == "Unaware":
        defense_stage = 0
        sp_defense_stage = 0

    if (attacker.ability == "Rivalry" and attacker.gender is not None
            and defender.gender is not None):
        if attacker.gender == defender.gender:
            move_power = c_div(move_power * 125, 100)
        else:
            move_power = c_div(move_power * 75, 100)

    if move in PUNCHING_MOVES and attacker.ability == "Iron Fist":
        move_power = c_div(move_power * 12, 10)

    weather_active = not any(p.ability in ("Cloud Nine", "Air Lock")
                             for p in actives)
    weather = battle.field.weather
    if weather_active:
        if weather == "sun" and attacker.ability == "Solar Power":
            sp_attack_stat = c_div(sp_attack_stat * 15, 10)
        if weather == "sand" and "Rock" in defender.types:
            sp_defense_stat = c_div(sp_defense_stat * 15, 10)
        # Flower Gift counts same-side battlers, which in singles includes
        # only the battler itself.
        if weather == "sun" and attacker.ability == "Flower Gift":
            attack_stat = c_div(attack_stat * 15, 10)
        if (weather == "sun" and attacker.ability != "Mold Breaker"
                and defender.ability == "Flower Gift"):
            sp_defense_stat = c_div(sp_defense_stat * 15, 10)

    if move in HALVE_DEFENSE_MOVES:
        defense_stat = c_div(defense_stat, 2)

    damage = 0
    if move_class == "Physical":
        damage = _stage_apply(attack_stat, attack_stage)
        damage *= move_power
        damage *= c_div(level * 2, 5) + 2
        stage_divisor = _stage_apply(defense_stat, defense_stage)
        damage = c_div(damage, stage_divisor)
        damage = c_div(damage, 50)

        if attacker.status == "brn" and attacker.ability != "Guts":
            damage = c_div(damage, 2)

        if defender_side.reflect and move not in REMOVE_SCREENS_MOVES:
            damage = c_div(damage, 2)
    elif move_class == "Special":
        damage = _stage_apply(sp_attack_stat, sp_attack_stage)
        damage *= move_power
        damage *= c_div(level * 2, 5) + 2
        stage_divisor = _stage_apply(sp_defense_stat, sp_defense_stage)
        damage = c_div(damage, stage_divisor)
        damage = c_div(damage, 50)

        if defender_side.light_screen and move not in REMOVE_SCREENS_MOVES:
            damage = c_div(damage, 2)

    if weather_active:
        if weather == "rain":
            if mtype == "Fire":
                damage = c_div(damage, 2)
            elif mtype == "Water":
                damage = c_div(damage * 15, 10)
        if weather == "sun":
            if mtype == "Fire":
                damage = c_div(damage * 15, 10)
            elif mtype == "Water":
                damage = c_div(damage, 2)
        # FIELD_CONDITION_SOLAR_DOWN halves vanilla SolarBeam in bad weather;
        # Kaizo's SolarBeam variants are ordinary moves, so it never applies.

    if "flash_fire" in attacker.volatiles and mtype == "Fire":
        damage = c_div(damage * 15, 10)

    return damage + 2


def _ignorable(attacker: Pokemon, defender: Pokemon, ability: str) -> bool:
    return attacker.ability != "Mold Breaker" and defender.ability == ability
