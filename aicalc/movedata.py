"""Lookup for Kaizo move properties, backed by data/moves.csv.

The Expert flag asks about moves the AI *knows about* rather than the move
being scored -- "was the foe's last move special?", "does the user have a
damaging move?" -- so it needs the move table, not just the Context.

Names are joined through data/move_aliases.json, since the scoring site and
the spreadsheet disagree on a couple of names (see data/README.md).
"""
from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent / "data"

HIGH_CRIT_MARKER = "high crit ratio"


@lru_cache(maxsize=1)
def _aliases() -> dict[str, str]:
    raw = json.loads((_DATA / "move_aliases.json").read_text())
    return {k: v for k, v in raw.items() if not k.startswith("_")}


@lru_cache(maxsize=1)
def _table() -> dict[str, dict[str, str]]:
    rows = {}
    with (_DATA / "moves.csv").open() as fh:
        for row in csv.DictReader(fh):
            name = row["Name"]
            if name and name != "-" and not name.isdigit():
                rows[name] = row
    return rows


def _row(move: str) -> dict[str, str] | None:
    table = _table()
    return table.get(_aliases().get(move, move)) or table.get(move)


def category(move: str | None) -> str | None:
    """'Physical', 'Special', 'Status', or None if the move is unknown."""
    row = _row(move) if move else None
    return row["Category"] if row else None


def is_damaging(move: str | None) -> bool:
    return category(move) in ("Physical", "Special")


def is_status(move: str | None) -> bool:
    return category(move) == "Status"


def priority(move: str | None) -> int:
    row = _row(move) if move else None
    return int(row["Priority"]) if row else 0


def base_pp(move: str | None) -> int:
    row = _row(move) if move else None
    return int(row["PP"]) if row else 0


def is_high_crit(move: str | None) -> bool:
    row = _row(move) if move else None
    return bool(row) and HIGH_CRIT_MARKER in row["Additional Effect"].lower()


def power(move: str | None) -> int:
    row = _row(move) if move else None
    return int(row["Power"]) if row else 0


def move_type(move: str | None) -> str | None:
    """The move's Kaizo type, e.g. 'Fire' or '???'."""
    row = _row(move) if move else None
    return row["Type"] if row else None


def vanilla_id(move: str | None) -> int | None:
    """The vanilla move-slot ID this Kaizo move occupies. The AI's
    special-power dispatch (Magnitude roll, Psywave roll, Return friendship,
    weight moves...) keys on this, since repurposed moves keep their slot."""
    row = _row(move) if move else None
    return int(row["ID Number"]) if row else None


def known(move: str) -> bool:
    return _row(move) is not None
