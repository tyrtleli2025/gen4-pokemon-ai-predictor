"""
Input: None
Output: A Battle object with attributes ai, player, field, and flags.  ai and player are Side objects. 
field is a Field object. flags is a set of active flags. 

The goal of this script is to describe the situation of a battle, including which Pokemon are on each side, the field conditions, etc. 
"""
from dataclasses import dataclass, field

# Volatile conditions a Pokemon can carry, as used in Pokemon.volatiles.
# These are the ones the Basic flag actually asks about; add as needed.
VOLATILES = frozenset({
    "confused", "infatuated", "trapped", "substitute", "leech_seed",
    "curse", "perish_song", "torment", "embargo", "gastro_acid",
    "focus_energy", "ingrain", "aqua_ring", "camouflage", "power_trick",
    "magnet_rise", "lock_on", "foresight", "miracle_eye", "imprison",
    "disable", "encore",
})


@dataclass
class Pokemon:
    species: str
    level: int
    ability: str
    item: str | None
    types: tuple[str, ...]
    stats: dict[str, int]        # keys: 'atk', 'def', 'spa', 'spd', 'spe'
    max_hp: int
    current_hp: int
    status: str | None = None    # 'psn', 'brn', 'par', 'slp', 'frz', 'tox', or None
    boosts: dict[str, int] = field(default_factory=dict)  # stat -> -6..+6
    moves: list[str] = field(default_factory=list)
    last_move: str | None = None  # move this Pokemon used last turn, or None
    protect_streak: int = 0       # consecutive turns a Protect-family move has succeeded
    gender: str | None = None     # 'M', 'F', or None for genderless
    volatiles: set[str] = field(default_factory=set)  # see VOLATILES
    turns_active: int = 1         # turns this Pokemon has been on the field (1 = just sent out)
    moves_used: set[str] = field(default_factory=set)  # for Last Resort
    consumed_item: str | None = None  # item already used up, for Recycle/Embargo

    def hp_percent(self) -> float:
        """Current HP as a percentage of max HP."""
        return self.current_hp / self.max_hp * 100


@dataclass
class Side:
    active: Pokemon
    party_remaining: int          # living Pokemon besides `active`
    hazards: dict[str, int] = field(default_factory=dict)   # 'spikes' -> 0..3, etc.
    reflect: bool = False
    light_screen: bool = False
    tailwind: bool = False
    safeguard: bool = False
    mist: bool = False
    lucky_chant: bool = False
    future_attack: bool = False   # Future Sight / Doom Desire pending on this side


@dataclass
class Field:
    weather: str | None = None    # 'sun', 'rain', 'sand', 'hail', 'fog', or None
    trick_room: bool = False
    turn: int = 1                 # 1 = first turn of the whole battle
    gravity: bool = False


@dataclass
class Battle:
    ai: Side
    player: Side
    field: Field
    flags: set[str] = field(default_factory=set)   # {'basic', 'expert', ...}
    doubles: bool = False
    frontier: bool = False        # Battle Frontier rules; out of scope, kept for one Embargo check


@dataclass
class Action:
    move: str
    target: str


def legal_actions(battle: Battle) -> list[Action]:
    """Enumerate the AI's candidate actions for the current turn.

    Singles only: one Action per known move, always targeting the player's
    active Pokemon.
    """
    return [Action(move=move, target="player") for move in battle.ai.active.moves]