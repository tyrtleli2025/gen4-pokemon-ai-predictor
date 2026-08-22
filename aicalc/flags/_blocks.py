"""Map moves to their scraped scoring block, per flag.

The scrape already answers "does this flag apply to this move, and with what
procedure" -- identical procedures were deduplicated into blocks. So a flag
module never re-derives move effects; it encodes each distinct block once,
keyed by a stable id, and this module routes moves to them.
"""
from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

_SCRAPE = Path(__file__).resolve().parent / "_scraped" / "per_move.json"

NO_PROCEDURE = "(No applicable AI procedures)"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def block_id(text: str) -> str:
    """Stable short id for a block, derived from its scraped text."""
    return hashlib.sha1(normalize(text).encode()).hexdigest()[:8]


@lru_cache(maxsize=1)
def _per_move() -> dict[str, dict[str, str]]:
    return json.loads(_SCRAPE.read_text())


@lru_cache(maxsize=1)
def all_moves() -> frozenset[str]:
    """Every canonical Kaizo move name (the scrape's key set)."""
    return frozenset(_per_move())


@lru_cache(maxsize=None)
def blocks_for_flag(flag: str) -> dict[str, tuple[str, tuple[str, ...]]]:
    """{block_id: (verbatim text, moves using it)} for one flag."""
    groups: dict[str, tuple[str, list[str]]] = {}
    for move, sections in _per_move().items():
        text = sections.get(flag, NO_PROCEDURE)
        if text == NO_PROCEDURE:
            continue
        bid = block_id(text)
        if bid not in groups:
            groups[bid] = (text, [])
        groups[bid][1].append(move)
    return {bid: (text, tuple(sorted(moves))) for bid, (text, moves) in groups.items()}


def block_id_for(flag: str, move: str) -> str | None:
    """The block a move uses for a flag, or None if the flag doesn't apply."""
    text = _per_move().get(move, {}).get(flag, NO_PROCEDURE)
    return None if text == NO_PROCEDURE else block_id(text)


def coverage(flag: str, encoded: dict) -> tuple[int, int, list[str]]:
    """(encoded count, total blocks, ids still missing) for a flag."""
    all_ids = set(blocks_for_flag(flag))
    missing = sorted(all_ids - set(encoded))
    return len(all_ids) - len(missing), len(all_ids), missing
