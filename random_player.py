from modgame import ModPlayer #noqa
import random


class RandomPlayer(ModPlayer):
    def take_turn(self, identifier: int, player_count: int) -> int:
        return random.choice(self.hand)
    
