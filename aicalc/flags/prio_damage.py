"""Prioritize Extremes / Prio Damage flag.

Blocks encoded: 1/1. Source text in _scraped/dedup.md; block ids from _blocks.py.
"""
from ..script import Add, Chance, Seq, Stop

# 7a96e66c -- 182 moves
#   "Unconditionally:
#    61% (156/256) chance of score +2 and terminate"
#
# Decomp (PrioritizeExtremes_Main): `IfRandomLessThan 100` jumps to terminate,
# so +2 lands on the fall-through at (256-100)/256 = 156/256 -- agrees with
# bparkpk exactly.
#
# "Unconditionally" is only unconditional *given the move*. The decomp guards
# the whole routine with `FlagMoveDamageScore / IfLoadedNotEqualTo
# AI_NO_COMPARISON_MADE`, i.e. it applies only to effects the AI cannot damage-
# compare (variable power, flat damage, or zero power). That guard is exactly
# what selects these 182 moves, so it lives in the move->block mapping rather
# than in this script.
UNCONDITIONAL_PLUS_2 = Chance(156, 256, Seq(Add(2), Stop()))

BLOCKS = {
    "7a96e66c": UNCONDITIONAL_PLUS_2,
}
