"""Compose all active flags into one ScoreDist per action.

Each flag runs its own script with its own RNG draws, and no flag's script
reads the score another flag produced (verified for all six encoded flags --
none contains a back-reference). The per-flag deltas are therefore independent
random variables, so the combined distribution is their convolution.

Every move starts from a base score of 100 (confirmed by the lhearachel gist).
That constant cannot change which action wins, but it is carried anyway so the
numbers match what the game is actually holding.
"""
from __future__ import annotations

from .dist import ScoreDist
from .flags import (basic, baton_pass, evaluate_attacks, expert, prio_damage,
                    setup_first_turn)
from .flags._blocks import block_id_for
from .predicates import Context, DamageBackend
from .script import evaluate
from .state import Action, Battle, legal_actions

BASE_SCORE = 100

#: The flags this engine can score. A battle carrying any other flag cannot be
#: evaluated correctly, so scoring refuses rather than silently under-counting.
FLAG_MODULES = {
    "basic": basic,
    "evaluate_attacks": evaluate_attacks,
    "expert": expert,
    "setup_first_turn": setup_first_turn,
    "prio_damage": prio_damage,
    "baton_pass": baton_pass,
}


class UnsupportedFlags(ValueError):
    """Raised when a battle uses flags that have not been encoded."""


def active_flags(battle: Battle) -> list[str]:
    """The battle's flags, in a stable order, rejecting unsupported ones."""
    unknown = sorted(set(battle.flags) - set(FLAG_MODULES))
    if unknown:
        raise UnsupportedFlags(
            f"battle uses unencoded flags {unknown}; "
            f"encoded flags are {sorted(FLAG_MODULES)}"
        )
    return [f for f in FLAG_MODULES if f in battle.flags]


def flag_distribution(flag: str, ctx: Context) -> ScoreDist:
    """One flag's score delta for one action. Zero if the flag has no
    procedure for that move."""
    block = block_id_for(flag, ctx.action.move)
    if block is None:
        return ScoreDist.certain(0)
    script = FLAG_MODULES[flag].BLOCKS.get(block)
    if script is None:
        raise KeyError(
            f"{flag}: block {block} for move {ctx.action.move!r} is not encoded"
        )
    return evaluate(script, ctx)


def score_distribution(
    battle: Battle,
    action: Action,
    damage: DamageBackend | None = None,
    include_base: bool = True,
) -> ScoreDist:
    """Exact distribution of the AI's final score for one action."""
    ctx = Context(battle=battle, action=action, damage=damage)
    total = ScoreDist.certain(BASE_SCORE if include_base else 0)
    for flag in active_flags(battle):
        total = total.convolve(flag_distribution(flag, ctx))
    return total


def action_score_distributions(
    battle: Battle,
    damage: DamageBackend | None = None,
    include_base: bool = True,
) -> dict[Action, ScoreDist]:
    """Score distribution for every action the AI could take."""
    return {
        action: score_distribution(battle, action, damage, include_base)
        for action in legal_actions(battle)
    }
