"""Gen 4 stat and experience math.

Integer formulas exactly as the game computes them; used to build trainer
Pokemon from data/trainers.json and imported save mons from raw values.
"""
from __future__ import annotations

#: nature -> (boosted stat, hindered stat); neutral natures map to (None, None).
NATURES: dict[str, tuple[str | None, str | None]] = {
    "Hardy": (None, None), "Lonely": ("atk", "def"), "Brave": ("atk", "spe"),
    "Adamant": ("atk", "spa"), "Naughty": ("atk", "spd"),
    "Bold": ("def", "atk"), "Docile": (None, None), "Relaxed": ("def", "spe"),
    "Impish": ("def", "spa"), "Lax": ("def", "spd"),
    "Timid": ("spe", "atk"), "Hasty": ("spe", "def"), "Serious": (None, None),
    "Jolly": ("spe", "spa"), "Naive": ("spe", "spd"),
    "Modest": ("spa", "atk"), "Mild": ("spa", "def"), "Quiet": ("spa", "spe"),
    "Bashful": (None, None), "Rash": ("spa", "spd"),
    "Calm": ("spd", "atk"), "Gentle": ("spd", "def"), "Sassy": ("spd", "spe"),
    "Careful": ("spd", "spa"), "Quirky": (None, None),
}

#: nature index (PID % 25) -> name, in the game's order.
NATURE_ORDER = (
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky",
)


def compute_stats(base: dict[str, int], ivs: dict[str, int],
                  evs: dict[str, int], level: int,
                  nature: str) -> tuple[int, dict[str, int]]:
    """(max_hp, {atk, def, spa, spd, spe}) from base stats and build values.

    base/ivs/evs use keys hp/atk/def/spa/spd/spe.
    """
    up, down = NATURES[nature]

    max_hp = ((2 * base["hp"] + ivs["hp"] + evs["hp"] // 4) * level // 100
              + level + 10)

    stats = {}
    for stat in ("atk", "def", "spa", "spd", "spe"):
        value = (2 * base[stat] + ivs[stat] + evs[stat] // 4) * level // 100 + 5
        if stat == up:
            value = value * 110 // 100
        elif stat == down:
            value = value * 90 // 100
        stats[stat] = value
    return max_hp, stats


# --- experience curves (for deriving box-mon levels from raw exp) -----------

def _medium_fast(n: int) -> int:
    return n ** 3


def _medium_slow(n: int) -> int:
    return 6 * n ** 3 // 5 - 15 * n ** 2 + 100 * n - 140


def _fast(n: int) -> int:
    return 4 * n ** 3 // 5


def _slow(n: int) -> int:
    return 5 * n ** 3 // 4


def _erratic(n: int) -> int:
    if n <= 50:
        return n ** 3 * (100 - n) // 50
    if n <= 68:
        return n ** 3 * (150 - n) // 100
    if n <= 98:
        return n ** 3 * ((1911 - 10 * n) // 3) // 500
    return n ** 3 * (160 - n) // 100


def _fluctuating(n: int) -> int:
    if n <= 15:
        return n ** 3 * ((n + 1) // 3 + 24) // 50
    if n <= 36:
        return n ** 3 * (n + 14) // 50
    return n ** 3 * (n // 2 + 32) // 50


EXP_RATES = {
    "MEDIUM_FAST": _medium_fast,
    "MEDIUM_SLOW": _medium_slow,
    "FAST": _fast,
    "SLOW": _slow,
    "ERRATIC": _erratic,
    "FLUCTUATING": _fluctuating,
}


def level_from_exp(exp: int, exp_rate: str) -> int:
    """The highest level whose curve requirement does not exceed exp."""
    curve = EXP_RATES[exp_rate]
    level = 1
    while level < 100 and curve(level + 1) <= exp:
        level += 1
    return level
