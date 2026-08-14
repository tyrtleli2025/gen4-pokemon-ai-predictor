"""Evaluate Attacks flag.

Blocks encoded: 9/9, reducing to 4 distinct script shapes. Source text in
_scraped/dedup.md; block ids from _blocks.py. Cross-checked against the decomp
in EvalAttack_Main (see _scraped/DECOMP_NOTES.md) -- fully confirmed, no
ambiguity survived.
"""
from ..script import Add, Chance, If, Seq, Stop

# Shape A -- ordinary damaging move.
#   "If the move can KO: +N and terminate.
#    Elif a different known move deals more damage: -1 and terminate.
#    Elif 4x effective: 68.8% (176/256) chance of +2 and terminate."
# N is 4 normally, 6 for the seven +1-priority-effect moves (Aqua Jet, Bullet
# Punch, Ice Shard, Mach Punch, Quick Attack, Shadow Sneak, Vacuum Wave).
# Decomp: EvalAttack_ApplyKillBonuses adds 2 (if effect == PRIORITY_1) THEN
# falls through into an unconditional +4 -- label fall-through, not a typo --
# giving +6 total for those seven moves and +4 for everything else. The kill
# branch never checks quad-effectiveness afterward (PopOrEnd right there),
# confirming "terminate" really means stop, matching bparkpk's text exactly.
def _standard(ko_bonus: int):
    return Seq(
        If(lambda c: c.can_ko(), Seq(Add(ko_bonus), Stop())),
        If(lambda c: not c.is_best_damaging_move(), Seq(Add(-1), Stop())),
        If(lambda c: c.effectiveness() == 4, Chance(176, 256, Seq(Add(2), Stop()))),
    )


STANDARD = _standard(4)
STANDARD_PRIORITY = _standard(6)

# Shape B -- status/non-damaging move: no KO or damage-comparison branch
# applies (0 base power), so the block reduces to the quad-effectiveness
# check alone. Decomp: IfCurrentMoveKills is always false at 0 power, and
# FlagMoveDamageScore returns AI_NO_COMPARISON_MADE (not AI_NOT_HIGHEST_DAMAGE)
# for non-damaging effects, so control falls straight through to
# EvalAttack_CheckQuadEffective.
STATUS_ONLY = If(lambda c: c.effectiveness() == 4, Chance(176, 256, Seq(Add(2), Stop())))

# Shape C -- Explosion, Focus Punch, Memento, Selfdestruct.
#   "Unconditionally: 80.1% (205/256) chance of -2 and continue.
#    If 4x effective: 68.8% (176/256) chance of +2 and terminate."
# No KO branch and no "-1 if outdamaged" branch appear in the scraped text for
# these four, and none is added here -- bparkpk describes actual observed
# behavior, not the vanilla control-flow shape. Decomp explains why a KO
# bonus is structurally absent for HALVE_DEFENSE (Explosion/Selfdestruct, and
# Memento since Kaizo repurposed it to this same effect): the kill branch
# special-cases this effect straight to Terminate with no bonus at all. Why
# the "-1 if outdamaged" branch is also absent (for these plus Focus Punch)
# is not fully resolved by decomp -- its own comment notes Focus Punch can
# never reach the kill-check branch in the first place, which is consistent
# but not a complete explanation. Encoded as scraped either way, per the rule
# that bparkpk wins on conditions.
SUICIDE_DEPRIORITIZE = Seq(
    Chance(205, 256, Add(-2)),
    If(lambda c: c.effectiveness() == 4, Chance(176, 256, Seq(Add(2), Stop()))),
)

BLOCKS = {
    "60e2d800": STANDARD,           # 256 moves, the general case
    "781e3ebe": STANDARD,           # 16 moves, multi-hit (single-hit-for-scoring note only)
    "f418975b": STANDARD,           # Bulldoze (Magnitude-calc note only)
    "bb46b7a1": STANDARD,           # Pound
    "6452539f": STANDARD,           # Return (102bp-for-scoring note only)
    "ec3405ca": STANDARD,           # Triple Axel (Psywave-calc note only)
    "469e0e0f": STANDARD_PRIORITY,  # the 7 +1-priority-effect moves
    "bfeba285": STATUS_ONLY,        # 179 status/0bp moves
    "06dd7390": SUICIDE_DEPRIORITIZE,  # Explosion, Focus Punch, Memento, Selfdestruct
}
