"""The AI's own damage layer: TrainerAI_CalcDamage (trainer_ai.c:2868),
TrainerAI_CalcAllDamage (:2799) and the AI commands built on them, exposed as
a real DamageBackend.

Randomness: Kaizo's Bulldoze (Magnitude's slot) and Triple Axel (Psywave's
slot) roll power INSIDE the AI's damage calc, fresh on every consultation.
Facts derived from them are therefore random variables. This backend computes
each fact under every joint outcome; when the outcomes agree it returns the
fact, and when they disagree it raises AmbiguousRandomDamage naming the move
and the JSON override to supply -- exact per-consultation Bernoulli modelling
is a documented follow-up (see DECOMP_NOTES.md).
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

from .. import movedata
from ..flags._blocks import block_id_for
from ..state import Action, Battle, Pokemon, Side
from .damage import calc_move_damage
from .divmath import c_div, game_divide
from .items import hold_effect
from .type_chart import (IMMUNE, SUPER_EFFECTIVE, apply_type_chart,
                         effectiveness_bucket)


class NeedsManualFact(ValueError):
    """The computed backend cannot answer; supply a JSON damage override."""


class AmbiguousRandomDamage(NeedsManualFact):
    pass


class NeedsPartyData(NeedsManualFact):
    pass


class NeedsWeightData(NeedsManualFact):
    pass


#: Magnitude power tiers with their roll probabilities (trainer_ai.c:3030).
MAGNITUDE_TIERS = (
    (Fraction(5, 100), 10), (Fraction(10, 100), 30), (Fraction(20, 100), 50),
    (Fraction(30, 100), 70), (Fraction(20, 100), 90), (Fraction(10, 100), 110),
    (Fraction(5, 100), 150),
)

#: sWeightToPower: (max weight in hectograms, power).
WEIGHT_TO_POWER = ((100, 20), (250, 40), (500, 60), (1000, 80), (2000, 100))


def comparable(move: str) -> bool:
    """Whether the move enters the AI's damage-comparison table.

    Derived from the scrape: the Prioritize Extremes flag applies exactly to
    the moves FlagMoveDamageScore marks AI_NO_COMPARISON_MADE (status moves,
    the sNoDamageCalcMoveEffects family, and power<=1 non-alt-power moves),
    so membership there is the Kaizo-correct exclusion set.
    """
    return block_id_for("prio_damage", move) is None


def _special_outcomes(battle: Battle, move: str, attacker: Pokemon,
                      attacker_side: Side,
                      defender: Pokemon, defender_side: Side):
    """TrainerAI_CalcDamage's special-power switch (trainer_ai.c:2885-3078),
    dispatched on the vanilla slot ID from moves.csv. Yields
    (probability, power, fixed_damage, move_type) tuples; power/fixed 0 mean
    "use the move data" / "run the real formula".
    """
    vid = movedata.vanilla_id(move)
    if vid == 237:  # Hidden Power -- IV-driven; no Kaizo move should hit this
        raise NeedsManualFact(f"{move}: Hidden Power IV calculation is not "
                              f"modelled; supply a damage override")
    if vid == 363:  # Natural Gift -- berry table not modelled
        raise NeedsManualFact(f"{move}: Natural Gift berry powers are not "
                              f"modelled; supply a damage override")
    if vid == 449:  # Judgment -- typed by held plate
        effect, _ = hold_effect(attacker.item)
        if (effect or "").startswith("boost_") and "plate" in str(attacker.item).lower():
            yield (Fraction(1), 0, 0, effect.split("_", 1)[1])
        else:
            yield (Fraction(1), 0, 0, "Normal")
        return
    if vid == 360:  # Gyro Ball
        from ..predicates import effective_speed
        atk_speed = effective_speed(attacker, attacker_side)
        def_speed = effective_speed(defender, defender_side)
        power = 1 + int(25 * def_speed / atk_speed)
        yield (Fraction(1), min(power, 150), 0, None)
        return
    if vid == 82:  # Dragon Rage
        yield (Fraction(1), 0, 40, None)
        return
    if vid in (69, 101):  # Seismic Toss, Night Shade
        yield (Fraction(1), 0, attacker.level, None)
        return
    if vid == 149:  # Psywave (Kaizo: Triple Axel)
        for roll in range(5, 16):
            yield (Fraction(1, 11), 0, c_div(attacker.level * roll, 10), None)
        return
    if vid == 216:  # Return
        friendship = 255 if attacker.friendship is None else attacker.friendship
        yield (Fraction(1), c_div(friendship * 10, 25), 0, None)
        return
    if vid == 218:  # Frustration (0 power at friendship 255 -> move data power)
        friendship = 255 if attacker.friendship is None else attacker.friendship
        yield (Fraction(1), c_div((255 - friendship) * 10, 25), 0, None)
        return
    if vid == 222:  # Magnitude (Kaizo: Bulldoze)
        for prob, power in MAGNITUDE_TIERS:
            yield (prob, power, 0, None)
        return
    if vid == 49:  # SonicBoom
        yield (Fraction(1), 0, 20, None)
        return
    if vid in (67, 447):  # Low Kick, Grass Knot
        if defender.weight_hg is None:
            raise NeedsWeightData(f"{move}: needs the defender's weight "
                                  f"(Pokemon.weight_hg) or a damage override")
        for max_weight, power in WEIGHT_TO_POWER:
            if defender.weight_hg <= max_weight:
                yield (Fraction(1), power, 0, None)
                return
        yield (Fraction(1), 120, 0, None)
        return
    yield (Fraction(1), 0, 0, None)


def damage_outcomes(battle: Battle, move: str, attacker: Pokemon,
                    attacker_side: Side, defender: Pokemon,
                    defender_side: Side, variance: int = 100
                    ) -> list[tuple[Fraction, int]]:
    """TrainerAI_CalcDamage: every possible damage value with its probability.
    Deterministic moves return a single outcome.
    """
    outcomes = []
    for prob, power, fixed, mtype in _special_outcomes(
            battle, move, attacker, attacker_side, defender, defender_side):
        if fixed == 0:
            damage = calc_move_damage(battle, move, attacker, defender,
                                      attacker_side, defender_side,
                                      power=power, move_type=mtype)
            ignore = False
        else:
            damage = fixed
            ignore = True
        damage, flags = apply_type_chart(battle, move, attacker, defender,
                                         damage, move_type=mtype,
                                         ignore_type_checks=ignore)
        if flags & IMMUNE:
            damage = 0
        else:
            damage = game_divide(damage * variance, 100)
        outcomes.append((prob, damage))
    return outcomes


def _ai_view(battle: Battle) -> tuple[Pokemon, Side, Pokemon, Side]:
    return (battle.ai.active, battle.ai, battle.player.active, battle.player)


def _unanimous(move: str, fact: str, values: list) -> bool:
    distinct = set(values)
    if len(distinct) == 1:
        return distinct.pop()
    raise AmbiguousRandomDamage(
        f"{move}: {fact} depends on the AI's internal power roll "
        f"(outcomes disagree); supply a damage override for this move"
    )


class CalcBackend:
    """DamageBackend computed from Battle state via the ported AI calc."""

    def can_ko(self, battle: Battle, action: Action) -> bool:
        # AICmd_IfCurrentMoveKills (trainer_ai.c:1525): gated on the same
        # eligibility as the damage comparison; ineligible moves never jump.
        if not comparable(action.move):
            return False
        attacker, atk_side, defender, def_side = _ai_view(battle)
        outcomes = damage_outcomes(battle, action.move, attacker, atk_side,
                                   defender, def_side)
        return _unanimous(action.move, "can_ko",
                          [defender.current_hp <= dmg for _, dmg in outcomes])

    def is_best_damaging_move(self, battle: Battle, action: Action) -> bool:
        if not comparable(action.move):
            raise AssertionError(
                f"{action.move}: is_best_damaging_move consulted for a move "
                f"outside the comparison table -- its block should not ask"
            )
        attacker, atk_side, defender, def_side = _ai_view(battle)
        per_move = {}
        for move in attacker.moves:
            if comparable(move):
                per_move[move] = damage_outcomes(battle, move, attacker,
                                                 atk_side, defender, def_side)
            else:
                per_move[move] = [(Fraction(1), 0)]

        moves = list(per_move)
        results = []
        for combo in product(*(per_move[m] for m in moves)):
            dmg = dict(zip(moves, (d for _, d in combo)))
            results.append(not any(dmg[m] > dmg[action.move] for m in moves))
        return _unanimous(action.move, "is_best_damaging_move", results)

    def effectiveness(self, battle: Battle, action: Action) -> float:
        attacker, _, defender, _ = _ai_view(battle)
        return effectiveness_bucket(battle, action.move, attacker, defender)

    def has_super_effective_move(self, battle: Battle) -> bool:
        # AI_HasSuperEffectiveMove (trainer_ai.c:3560) with the deterministic
        # flag: chart applied at damage 0, checking the net SE *flag* (so only
        # power>0 moves can qualify, and dual-type SE+NVE cancels out).
        attacker, _, defender, _ = _ai_view(battle)
        for move in attacker.moves:
            _, flags = apply_type_chart(battle, move, attacker, defender, 0)
            if flags & SUPER_EFFECTIVE:
                return True
        return False

    def party_member_outdamages(self, battle: Battle) -> bool:
        raise NeedsPartyData(
            "party_member_outdamages needs party-member movesets the schema "
            "does not carry; supply the damage.party_member_outdamages "
            "override in the case file"
        )

    def target_last_move_outdamages(self, battle: Battle) -> bool:
        # AICmd_IfBattlerDealsMoreDamage (trainer_ai.c:2188). Vanilla quirk
        # ported verbatim: the target's last move is calculated with the
        # target as BOTH attacker and defender (TrainerAI_CalcDamage always
        # defends with AI_CONTEXT.defender).
        attacker, atk_side, defender, def_side = _ai_view(battle)
        if defender.last_move is None:
            return False

        per_move = []
        for move in attacker.moves:
            if comparable(move):
                per_move.append(damage_outcomes(battle, move, attacker,
                                                atk_side, defender, def_side))
            else:
                per_move.append([(Fraction(1), 0)])
        target_outcomes = damage_outcomes(battle, defender.last_move, defender,
                                          def_side, defender, def_side)

        results = []
        for combo in product(target_outcomes, *per_move):
            target_dmg = combo[0][1]
            ai_max = max(d for _, d in combo[1:]) if len(combo) > 1 else 0
            results.append(target_dmg > ai_max)
        return _unanimous(defender.last_move, "target_last_move_outdamages",
                          results)


class OverrideBackend:
    """CalcBackend with per-fact overrides from a case file's damage section.

    Any fact present in the overrides wins; everything else is computed.
    """

    def __init__(self, base, move_facts: dict[str, dict] | None = None,
                 best: frozenset[str] | None = None,
                 has_super_effective: bool | None = None,
                 party_outdamages: bool | None = None,
                 last_move_outdamages: bool | None = None):
        self._base = base
        self._move_facts = move_facts or {}
        self._best = best
        self._has_se = has_super_effective
        self._party_out = party_outdamages
        self._last_out = last_move_outdamages

    def can_ko(self, battle, action):
        facts = self._move_facts.get(action.move, {})
        if "can_ko" in facts:
            return facts["can_ko"]
        return self._base.can_ko(battle, action)

    def is_best_damaging_move(self, battle, action):
        if self._best is not None:
            return action.move in self._best
        return self._base.is_best_damaging_move(battle, action)

    def effectiveness(self, battle, action):
        facts = self._move_facts.get(action.move, {})
        if "effectiveness" in facts:
            return facts["effectiveness"]
        return self._base.effectiveness(battle, action)

    def has_super_effective_move(self, battle):
        if self._has_se is not None:
            return self._has_se
        return self._base.has_super_effective_move(battle)

    def party_member_outdamages(self, battle):
        if self._party_out is not None:
            return self._party_out
        return self._base.party_member_outdamages(battle)

    def target_last_move_outdamages(self, battle):
        if self._last_out is not None:
            return self._last_out
        return self._base.target_last_move_outdamages(battle)
