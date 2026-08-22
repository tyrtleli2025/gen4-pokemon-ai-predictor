"""Risky flag.

Blocks encoded: 1/1. Source text in _scraped/dedup.md; block ids from
_blocks.py.

Single rule across all 61 eligible moves:
  "Unconditionally: 50% (128/256) chance of score +2 and terminate"

Decomp (Risky_Main) confirms both halves: the routine is gated on the move's
effect being in the Risky_RiskyEffects table (sleep, Selfdestruct/Explosion's
halve-defense effect, OHKO, high-crit, confusion, Metronome-likes, Psywave-like
random damage) -- that gate is what selects the 61 moves and lives in the
move->block mapping, not here -- and `IfRandomLessThan 128` jumps to terminate,
so the +2 sits on the fall-through at (256-128)/256 = 50%. Kaizo additionally
routes Triple Axel and Fury Cutter through this flag (per data/ai_changes.csv);
both appear in the scraped move list, so the mapping already covers them.
"""
from ..script import Add, Chance, Seq, Stop

FIFTY_FIFTY_PLUS_2 = Chance(128, 256, Seq(Add(2), Stop()))

BLOCKS = {
    "d4faa70a": FIFTY_FIFTY_PLUS_2,
}
