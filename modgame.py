import random  # noqa: F401



def evaluate_round(card1: int, card2: int):
    """
    Evaluates the winner between the two cards.

    Returns:
        1 if card 1 wins, 2 if card 2 wins, 0 if no one won.
    """
    if (card1 - card2) % 10 == 1:
        return 1
    elif (card2 - card1) % 10 == 1:
        return 2
    return 0


class ModPlay:
    def __init__(self, rank: str, player_id: int) -> None:
        self.rank = rank
        self.player_id = player_id

    def __str__(self) -> str:
        return f"({self.rank}) played by {self.player_id}"


class ModPlayer:
    """class that should be inherited from for each unique Player."""    
    def start_game(self, identifier: int, player_count: int):
        pass

    def take_turn(self, identifier: int, player_count: int):
        pass
    
    def observe_play(self, identifier: int, player_count: int):
        pass
    
    
    

class ModController:
    RANKS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] #noqa
    RANK_STRENGTH = {rank: i for i, rank in enumerate(RANKS)} #noqa

    def __init__(self):
        self._players = []
    
    def join(self, player):
        if player not in self._players:
            self._players.append(player)


def repeated_games(n: int):
    return n 