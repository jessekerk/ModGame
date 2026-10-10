from modgame import ModPlayer #noqa
from typing import List

class RandomPlayer(ModPlayer):
    def start_game(self, identifier: int, initial_hand: List[int]):
        super().start_game(self, identifier, initial_hand)

    def take_turn(self):
        import random
        card = random.choice(self.hand)
        self.hand.remove(card)
        return card
    
    def observe_play(self, identifier: int, player_count: int, card: str):
        pass
