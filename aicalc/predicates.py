"""Context class answering the AI's derived questions for a Battle/Action pair."""
from dataclasses import dataclass
from fractions import Fraction
from typing import Protocol

from .state import Action, Battle, Pokemon, Side

PROTECT_LIKE_MOVES = {"Protect", "Detect"}


def _stage_multiplier(stage: int) -> Fraction:
    stage = max(-6, min(6, stage))
    if stage >= 0:
        return Fraction(2 + stage, 2)
    return Fraction(2, 2 - stage)


class DamageBackend(Protocol):
    """Hand-supplied answers to damage-dependent questions, until the real
    damage calculator (calc/) exists.
    """

    def can_ko(self, battle: Battle, action: Action) -> bool: ...
    def is_best_damaging_move(self, battle: Battle, action: Action) -> bool: ...
    def effectiveness(self, battle: Battle, action: Action) -> float: ...


@dataclass
class Context:
    battle: Battle
    action: Action
    damage: DamageBackend | None = None

    @property
    def user(self) -> Pokemon:
        return self.battle.ai.active

    @property
    def target(self) -> Pokemon:
        return self.battle.player.active

    @property
    def user_side(self) -> Side:
        return self.battle.ai

    @property
    def target_side(self) -> Side:
        return self.battle.player

    def is_first_turn(self) -> bool:
        """True on the first turn of the entire battle, not the first turn
        this Pokemon has been active.
        """
        return self.battle.field.turn == 1

    def knows_move(self, pokemon: Pokemon, move: str) -> bool:
        return move in pokemon.moves

    def has_ability(self, pokemon: Pokemon, ability: str) -> bool:
        return pokemon.ability == ability

    def has_type(self, pokemon: Pokemon, type_: str) -> bool:
        return type_ in pokemon.types

    def has_status(self, pokemon: Pokemon, status: str) -> bool:
        return pokemon.status == status

    def boost_stage(self, pokemon: Pokemon, stat: str) -> int:
        return pokemon.boosts.get(stat, 0)

    def weather_is(self, weather: str) -> bool:
        return self.battle.field.weather == weather

    def hazard_layers(self, side: Side, hazard: str) -> int:
        return side.hazards.get(hazard, 0)

    def last_move(self, pokemon: Pokemon) -> str | None:
        return pokemon.last_move

    def used_protect_last(self, pokemon: Pokemon) -> bool:
        return pokemon.last_move in PROTECT_LIKE_MOVES

    def protect_streak(self, pokemon: Pokemon) -> int:
        return pokemon.protect_streak

    def _effective_speed(self, pokemon: Pokemon, side: Side) -> Fraction:
        speed = Fraction(pokemon.stats["spe"]) * _stage_multiplier(pokemon.boosts.get("spe", 0))
        if pokemon.status == "par":
            speed *= Fraction(1, 4)
        if side.tailwind:
            speed *= 2
        return speed

    def user_is_faster(self) -> bool | None:
        """True if the AI's Pokemon moves before the target this turn, False
        if after, None on an exact speed tie. Accounts for boosts, paralysis,
        Tailwind, and Trick Room.
        """
        user_speed = self._effective_speed(self.user, self.user_side)
        target_speed = self._effective_speed(self.target, self.target_side)
        if user_speed == target_speed:
            return None
        faster = user_speed > target_speed
        return not faster if self.battle.field.trick_room else faster

    def can_ko(self) -> bool:
        if self.damage is None:
            raise NotImplementedError("no damage backend supplied")
        return self.damage.can_ko(self.battle, self.action)

    def is_best_damaging_move(self) -> bool:
        if self.damage is None:
            raise NotImplementedError("no damage backend supplied")
        return self.damage.is_best_damaging_move(self.battle, self.action)

    def effectiveness(self) -> float:
        if self.damage is None:
            raise NotImplementedError("no damage backend supplied")
        return self.damage.effectiveness(self.battle, self.action)
