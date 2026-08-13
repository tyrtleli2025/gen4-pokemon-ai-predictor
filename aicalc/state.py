"""
Input: None
Output: A Battle object with attributes ai, player, field, and flags.  ai and player are Side objects. 
field is a Field object. flags is a set of active flags. 

The goal of this script is to describe the situation of a battle, including which Pokemon are on each side, the field conditions, etc. 
"""
from dataclasses import dataclass, field


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


@dataclass
class Field:
    weather: str | None = None    # 'sun', 'rain', 'sand', 'hail', or None
    trick_room: bool = False
    turn: int = 1                 # 1 = first turn of the whole battle


@dataclass
class Battle:
    ai: Side
    player: Side
    field: Field
    flags: set[str] = field(default_factory=set)   # {'basic', 'expert', ...}


@dataclass
class Action:
    move: str
    target: str