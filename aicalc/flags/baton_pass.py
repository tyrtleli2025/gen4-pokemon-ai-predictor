"""Baton Pass flag.

Blocks encoded: 6/6. Source text in _scraped/dedup.md; block ids from
_blocks.py. Cross-checked against the decomp's BatonPass_Main (see
_scraped/DECOMP_NOTES.md); two of the six blocks (95347291, and the
first-turn parenthetical in 5d652fe9) have no vanilla equivalent to check
against and are encoded via best-faith literal reading of bparkpk alone --
flagged individually below.
"""
from ..predicates import PROTECT_LIKE_MOVES
from ..script import Add, Chance, If, Seq, Stop

# Every block opens with the same two gates. Decomp confirms both: no living
# party members -> PopOrEnd with score unchanged (BatonPass_Terminate); and if
# the user doesn't know Baton Pass, a *single* random check for a no-op that is
# skipped entirely when the user does know it (IfMoveEffectKnown jumps past the
# roll straight to BatonPass_EvalMove) -- not a complementary in/out pair
# within one roll.
_NO_PARTY = If(lambda c: c.user_side.party_remaining == 0, Stop())


def _unknown_bp_gate(numerator: int, denominator: int = 256):
    return If(lambda c: not c.knows_move(c.user, "Baton Pass"),
              Chance(numerator, denominator, Stop()))


def _hp_tail():
    """Shared ending for the two "boost at high HP" blocks: +5 on turn 1,
    else -10 below 60% HP, else +1. Matches BatonPass_SetupAtHighHP exactly --
    linear cascade, not nested (LoadTurnCount==0 check, then a plain
    IfHPPercentLessThan/else pair).
    """
    return Seq(
        If(lambda c: c.is_first_turn(), Seq(Add(5), Stop())),
        If(lambda c: c.user.hp_percent() < 60, Seq(Add(-10), Stop())),
        Seq(Add(1), Stop()),
    )


# 28caf3f3 -- 159 moves, the generic case.
# "92% (235/256) chance of score +3 and terminate" -- matches BatonPass_EvalMove's
# generic tail (IfRandomLessThan 20, Risky_Terminate; AddToMoveScore 3) exactly.
GENERIC = Seq(_NO_PARTY, _unknown_bp_gate(81), Chance(235, 256, Seq(Add(3), Stop())))

# 5d652fe9 -- 6 moves. Same generic shape, but "(if first turn: +8 instead of
# +3)". Read as a substitution within the same 235/256 roll (same odds, larger
# prize on turn 1), not a separate gate -- no vanilla equivalent exists for
# this parenthetical (BatonPass_EvalMove's generic path has no LoadTurnCount
# check at all), so this reading is a best-faith one, not decomp-confirmed.
GENERIC_FIRST_TURN_BONUS = Seq(
    _NO_PARTY,
    _unknown_bp_gate(81),
    If(lambda c: c.is_first_turn(),
       Chance(235, 256, Seq(Add(8), Stop())),
       Chance(235, 256, Seq(Add(3), Stop()))),
)

# 054f1363 -- 6 moves (Swords Dance, Dragon Dance, Calm Mind, Nasty Plot, plus
# Aqua Ring and Tail Glow, which the decomp's explicit MOVE_* dispatch list
# does not include -- Kaizo evidently routes these two here as well; not
# something decomp can confirm, but the resulting script shape it does confirm
# matches bparkpk's text exactly).
SETUP_AT_HIGH_HP = Seq(_NO_PARTY, _unknown_bp_gate(81), _hp_tail())

# 95347291 -- Assist, Toxic. No decomp equivalent at all (no MOVE_ASSIST/
# MOVE_TOXIC special-casing in BatonPass_Main); this is Kaizo-specific new
# logic. Encoded via the most direct literal reading: on turn 1, 92% (235/256)
# chance of +8 and stop, else falls through to the same HP tail as
# SETUP_AT_HIGH_HP; off turn 1, 92.58% (237/256) chance of +3 which explicitly
# "continues" into that same HP tail either way. The ambiguity that decomp
# could not resolve: whether the complementary ~8% miss on turn 1 also falls
# through to the HP tail (assumed here, for consistency with the explicit
# "continue" wording used on the non-first-turn branch) or terminates blank.
ASSIST_TOXIC = Seq(
    _NO_PARTY,
    _unknown_bp_gate(79),
    If(lambda c: c.is_first_turn(),
       Chance(235, 256, Seq(Add(8), Stop())),
       Chance(237, 256, Add(3))),
    _hp_tail(),
)

# 47e2ff4e -- Baton Pass itself. No "doesn't know Baton Pass" gate (the move
# being scored *is* Baton Pass). Decomp (BatonPass_EvalBatonPass) confirms this
# is a strict priority cascade -- first matching check wins and terminates,
# via shared ScorePlus/ScoreMinus labels that each end in PopOrEnd -- not
# independent checks whose bonuses could stack.
BATON_PASS_ITSELF = Seq(
    _NO_PARTY,
    If(lambda c: c.is_first_turn(), Seq(Add(-2), Stop())),
    If(lambda c: c.boost_stage(c.user, "atk") >= 3, Seq(Add(3), Stop())),
    If(lambda c: c.boost_stage(c.user, "atk") == 2, Seq(Add(2), Stop())),
    If(lambda c: c.boost_stage(c.user, "atk") == 1, Seq(Add(1), Stop())),
    If(lambda c: c.boost_stage(c.user, "spa") >= 3, Seq(Add(3), Stop())),
    If(lambda c: c.boost_stage(c.user, "spa") == 2, Seq(Add(2), Stop())),
    If(lambda c: c.boost_stage(c.user, "spa") == 1, Seq(Add(1), Stop())),
)

# 3e751284 -- Detect, Protect. Matches BatonPass_EvalProtect exactly: the only
# use of last-move-used in this flag.
PROTECT_DETECT = Seq(
    _NO_PARTY,
    _unknown_bp_gate(81),
    If(lambda c: c.last_move(c.user) in PROTECT_LIKE_MOVES,
       Seq(Add(-2), Stop()),
       Seq(Add(2), Stop())),
)

BLOCKS = {
    "28caf3f3": GENERIC,
    "5d652fe9": GENERIC_FIRST_TURN_BONUS,
    "054f1363": SETUP_AT_HIGH_HP,
    "95347291": ASSIST_TOXIC,
    "47e2ff4e": BATON_PASS_ITSELF,
    "3e751284": PROTECT_DETECT,
}
