"""Canonicalise display spellings of move and flag names.

The engine keys everything on the scraped site's move names ("ThunderPunch",
"Selfdestruct"), but humans transcribe from UIs that spell them differently
("Thunder Punch", "Self-Destruct"). Matching ignores case, spaces and
punctuation. The one genuine collision -- Solar-Beam and SolarBeam are two
distinct Kaizo moves -- raises AmbiguousName rather than guessing.
"""
from __future__ import annotations

import difflib
import re
from functools import lru_cache

from .flags._blocks import all_moves


class UnknownName(ValueError):
    pass


class AmbiguousName(UnknownName):
    pass


#: Display spellings for the encoded flags, keyed by squash().
_FLAG_SPELLINGS = {
    "basic": "basic",
    "evaluateatks": "evaluate_attacks",
    "evaluateattacks": "evaluate_attacks",
    "evalatt": "evaluate_attacks",
    "expert": "expert",
    "1stturnsetup": "setup_first_turn",
    "firstturnsetup": "setup_first_turn",
    "setupfirstturn": "setup_first_turn",
    "priodamage": "prio_damage",
    "prioritydamage": "prio_damage",
    "prioritizeextremes": "prio_damage",
    "batonpass": "baton_pass",
    "risky": "risky",
}

_FLAG_DISPLAY = ("Basic", "Evaluate Atks", "Expert", "1st Turn Setup",
                 "Prio Damage", "Baton Pass", "Risky")


def squash(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


@lru_cache(maxsize=1)
def _move_index() -> dict[str, tuple[str, ...]]:
    index: dict[str, tuple[str, ...]] = {}
    for move in all_moves():
        key = squash(move)
        index[key] = index.get(key, ()) + (move,)
    return index


def canonical_move(name: str) -> str:
    """The scrape's canonical name for a possibly display-spelled move."""
    if name in all_moves():
        return name
    matches = _move_index().get(squash(name), ())
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        both = " and ".join(repr(m) for m in sorted(matches))
        raise AmbiguousName(
            f"{name!r} matches {both}, which are distinct Kaizo moves; "
            f"write the exact name"
        )
    close = difflib.get_close_matches(name, all_moves(), n=1)
    hint = f"; did you mean {close[0]!r}?" if close else ""
    raise UnknownName(f"unknown move {name!r}{hint}")


def canonical_flag(name: str) -> str:
    """The engine's flag id for a possibly display-spelled flag name."""
    flag = _FLAG_SPELLINGS.get(squash(name))
    if flag is None:
        accepted = ", ".join(_FLAG_DISPLAY)
        raise UnknownName(
            f"unknown flag {name!r}; accepted: {accepted} (or snake_case ids)"
        )
    return flag
