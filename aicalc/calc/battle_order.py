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

No crit support yet -- these are the non-crit lists (crit lands with the
turn recorder, Milestone C).
"""
from __future__ import annotations

from fractions import Fraction

from ..state import Battle, Pokemon, Side
from .ai_damage import _special_outcomes
from .damage import calc_move_damage
from .divmath import c_div
from .type_chart import IMMUNE, apply_type_chart


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
            rolls = []
            for variance in range(85, 101):
                dmg = c_div(base * variance, 100)
                dmg, flags = apply_type_chart(battle, move, attacker,
                                              defender, dmg, move_type=mtype)
                rolls.append(0 if flags & IMMUNE else dmg)
            desc = f"power {power}" if power else None
        outcomes.append((prob, desc, rolls))

    if len(outcomes) == 1:  # deterministic move: nothing to label
        prob, _, rolls = outcomes[0]
        return [(prob, None, rolls)]
    return outcomes
