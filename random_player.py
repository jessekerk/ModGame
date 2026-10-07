from modgame import ModPlayer #noqa

class RandomPlayer(ModPlayer):
    def start_game(self, identifier: int, player_count: int):
        super().start_game(identifier, player_count)

    def take_turn(self, identifier: int, player_count: int):
        import random
        card = random.choice(self.hand)
        self.hand.remove(card)
        return card
    
    def observe_play(self, identifier: int, player_count: int, card: str):
        pass
