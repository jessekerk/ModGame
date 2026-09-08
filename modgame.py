import random  # noqa: F401


class ModPlay:
    def __init__(self, rank: str, suit: str, player_id: int) -> None:
        self.rank = rank
        self.suit = suit
        self.player_id = player_id

    def __str__(self) -> str:
        return f"({self.rank}, {self.suit}) played by {self.player_id}"


class ModPlayer:
    """class that should be inherited from for each unique Player."""    
    def start_game(self, identifier: int, player_count: int):
        pass

    def take_turn(self, identifier: int, player_count: int):
        pass
    
    def observe_play(self, identifier: int, player_count: int):
        pass
    
    
    

class ModController:
    SUITS = ["♠", "♣", "♥", "♦"]    #noqa
    RANKS = ["J", "Q", "K", "A", "7", "8", "9", "10"] #noqa
    RANK_STRENGTH = {rank: i for i, rank in enumerate(RANKS)} #noqa

    def __init__(self):
        self._players = []
    
    def join(self, player):
        if player not in self._players:
            self._players.append(player)


def repeated_games(n: int):
    return n 