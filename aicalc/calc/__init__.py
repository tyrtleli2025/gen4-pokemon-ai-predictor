"""AI-side damage calculator, ported from the pret/pokeplatinum decomp.

This is the damage model the trainer AI itself runs (TrainerAI_CalcDamage and
friends), not the player-facing calculator: max-roll KO checks, single-hit
scoring for multi-hit moves, substitute powers for alt-power moves, and the
comparable-damage table that zeroes out suicide/charge/recharge moves.
"""
from .ai_damage import (AmbiguousRandomDamage, CalcBackend, NeedsManualFact,
                        NeedsPartyData, NeedsWeightData, OverrideBackend)

__all__ = [
    "AmbiguousRandomDamage", "CalcBackend", "NeedsManualFact",
    "NeedsPartyData", "NeedsWeightData", "OverrideBackend",
]
