"""Battle-order damage rolls: what a move will actually deal on screen.

ai_damage.py models the AI's own view (max-roll, variance after the chart).
The battle engine itself applies the 16-way variance BEFORE
BattleSystem_ApplyTypeChart: base formula (weather multipliers included)
-> damage * (85..100) / 100 -> STAB -> type chart. Validated digit-for-digit
against the HZLA Platinum Kaizo calculator's roll lists (L24 Muscle Band
Ludicolo in rain vs L20 Farfetch'd: Ice Punch 42,42,42,44,44,44,44,46,46,46,
46,48,48,48,48,50 -- and Aqua Cutter 33..40, proving rain's 1.5x lands inside
the base formula while STAB lands after the variance).

Fixed-damage moves (Dragon Rage, Seismic Toss, Kaizo Triple Axel...) take no
variance: all 16 "rolls" are the fixed value, zeroed on immunity.

Two battle-script-layer item effects apply here and ONLY here (the AI's
TrainerAI_CalcDamage contains neither, so the AI's own view stays blind to
both): the attacker's Life Orb multiplies the formula output by 1.3 before
the variance (BtlCmd_CalcDamage, battle_script.c:1346), and the defender's
type-resist berry halves each final roll (subscript_type_resist_berry:
game-divide by 2 on a super-effective hit of the berry's type -- Chilan on
any Normal hit -- suppressed by the defender's Klutz or Embargo via
Battler_HeldItem). Fixed-damage moves skip both, exactly as in the game:
their scripts bypass BtlCmd_CalcDamage, and the berry subscript bails on
SYSCTL_IGNORE_TYPE_CHECKS.

No crit support yet -- these are the non-crit lists (crit lands with the
turn recorder, Milestone C).
"""
from __future__ import annotations

from fractions import Fraction

from .. import movedata
from ..state import Battle, Pokemon, Side
from .ai_damage import _special_outcomes
from .damage import calc_move_damage
from .divmath import c_div, game_divide
from .items import hold_effect, weaken_berry
from .type_chart import IMMUNE, SUPER_EFFECTIVE, apply_type_chart


def _active_weaken_berry(defender: Pokemon) -> tuple[str, bool] | None:
    """The defender's resist berry, unless Klutz or Embargo suppress the
    held item entirely (Battler_HeldItem, battle_lib.c:5352)."""
    if defender.ability == "Klutz" or "embargo" in defender.volatiles:
        return None
    return weaken_berry(defender.item)


def battle_damage_outcomes(
        battle: Battle, move: str, attacker: Pokemon, attacker_side: Side,
        defender: Pokemon, defender_side: Side,
) -> list[tuple[Fraction, str | None, list[int]]]:
    """Every battle-order outcome of `move`: (probability, description,
    16 damage rolls in variance order, 85% first). The description is None
    unless the move's power/damage is itself rolled at use time (Bulldoze
    tiers, Triple Axel), in which case each entry is labelled.
    """
    outcomes = []
    for prob, power, fixed, mtype in _special_outcomes(
            battle, move, attacker, attacker_side, defender, defender_side):
        if fixed:
            _, flags = apply_type_chart(battle, move, attacker, defender,
                                        fixed, move_type=mtype,
                                        ignore_type_checks=True)
            rolls = [0 if flags & IMMUNE else fixed] * 16
            desc = f"{fixed} fixed"
        else:
            base = calc_move_damage(battle, move, attacker, defender,
                                    attacker_side, defender_side,
                                    power=power, move_type=mtype)
            atk_effect, atk_item_power = hold_effect(attacker.item)
            if (atk_effect == "life_orb" and attacker.ability != "Klutz"
                    and "embargo" not in attacker.volatiles):
                base = c_div(base * (100 + atk_item_power), 100)

            berry = _active_weaken_berry(defender)
            if attacker.ability == "Normalize":
                resolved_type = "Normal"
            else:
                resolved_type = mtype or movedata.move_type(move)

            rolls = []
            for variance in range(85, 101):
                dmg = c_div(base * variance, 100)
                dmg, flags = apply_type_chart(battle, move, attacker,
                                              defender, dmg, move_type=mtype)
                if flags & IMMUNE:
                    dmg = 0
                elif berry is not None:
                    berry_type, needs_se = berry
                    if (resolved_type == berry_type
                            and (not needs_se or flags & SUPER_EFFECTIVE)):
                        dmg = game_divide(dmg, 2)
                rolls.append(dmg)
            desc = f"power {power}" if power else None
        outcomes.append((prob, desc, rolls))

    if len(outcomes) == 1:  # deterministic move: nothing to label
        prob, _, rolls = outcomes[0]
        return [(prob, None, rolls)]
    return outcomes
