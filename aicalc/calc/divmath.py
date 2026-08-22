"""Integer arithmetic matching the game's C exactly.

C's `/` truncates toward zero; Python's `//` floors. All damage quantities in
the ported formula are non-negative, where the two agree, but these helpers
keep the semantics explicit and handle the game's special division.
"""
from __future__ import annotations


def c_div(dividend: int, divisor: int) -> int:
    """C integer division: truncation toward zero."""
    quotient = abs(dividend) // abs(divisor)
    if (dividend < 0) != (divisor < 0):
        quotient = -quotient
    return quotient


def game_divide(dividend: int, divisor: int) -> int:
    """BattleSystem_Divide (battle_lib.c:3599): C division, except a nonzero
    dividend never rounds to zero -- it clamps to +/-1 instead."""
    if dividend == 0:
        return 0
    signed_floor = -1 if dividend < 0 else 1
    quotient = c_div(dividend, divisor)
    return signed_floor if quotient == 0 else quotient
