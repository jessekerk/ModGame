"""A random baseline agent for the Mod game."""
import random

from modgame import ModPlayer


class RandomPlayer(ModPlayer):
    def __init__(self, name: str = "Random Player") -> None:
        super().__init__(name)

    def take_turn(self) -> int:
        card = random.choice(self.hand)
        self.hand.remove(card)
        return card
