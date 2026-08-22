"""Argmax with tie-breaking; tie-count DP.

The AI computes every action's final score and picks the highest, breaking
ties uniformly at random (confirmed by the lhearachel gist). Each action's
score is an independent random variable given by its ScoreDist, so the pick
probabilities come from enumerating the joint outcomes.

This is the naive subset enumeration from the plan: the product of the
actions' support sizes stays tiny for real battles (four moves, each with a
handful of outcomes). The tie-count DP replaces this only if it ever becomes
slow.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

from .dist import ScoreDist
from .predicates import DamageBackend
from .scoring import action_score_distributions
from .state import Action, Battle


def action_probabilities(dists: dict[Action, ScoreDist]) -> dict[Action, Fraction]:
    """Exact probability that each action ends up chosen."""
    if not dists:
        return {}
    actions = list(dists)
    result = {action: Fraction(0) for action in actions}
    per_action_outcomes = [list(dists[action].table.items()) for action in actions]

    for combo in product(*per_action_outcomes):
        joint = Fraction(1)
        for _, p in combo:
            joint *= p
        best = max(score for score, _ in combo)
        winners = [a for a, (score, _) in zip(actions, combo) if score == best]
        share = joint / len(winners)
        for winner in winners:
            result[winner] += share

    total = sum(result.values(), Fraction(0))
    if total != 1:
        raise AssertionError(f"pick probabilities sum to {total}, not 1")
    return result


def move_probabilities(
    battle: Battle,
    damage: DamageBackend | None = None,
) -> dict[Action, Fraction]:
    """The whole pipeline: Battle in, exact pick distribution out."""
    return action_probabilities(action_score_distributions(battle, damage))
