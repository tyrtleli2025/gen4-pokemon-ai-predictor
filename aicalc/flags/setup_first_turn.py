"""Setup First Turn flag.

Blocks encoded: 1/1. Source text in _scraped/dedup.md; block ids from _blocks.py.
"""
from ..script import Add, Chance, If, Seq, Stop

# 077f03b8 -- 91 moves
#   "If it is the first turn of battle:
#    68.75% (176/256) chance of score +2 and terminate"
#
# Decomp (SetupFirstTurn_Main): linear, no nesting ambiguity. Two points
# confirmed rather than assumed:
#   - `LoadTurnCount / IfLoadedNotEqualTo 0` means the first turn of the *whole
#     battle*, not the first turn this Pokemon is out -- matches Field.turn == 1.
#   - `IfRandomLessThan 80` jumps to terminate, so the +2 sits on the
#     fall-through path at (256-80)/256 = 176/256, agreeing with bparkpk.
# Which moves qualify is the decomp's SetupFirstTurn_SetupEffects table; we take
# that from the scrape's move->block mapping instead, which is Kaizo-correct
# (the vanilla table lists BATTLE_EFFECT_CONVERSION, dead in Kaizo).
FIRST_TURN_SETUP = If(
    lambda ctx: ctx.is_first_turn(),
    Chance(176, 256, Seq(Add(2), Stop())),
)

BLOCKS = {
    "077f03b8": FIRST_TURN_SETUP,
}
