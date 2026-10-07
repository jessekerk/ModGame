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
        return f"card ({self.rank}) played by player {self.player_id}"


class ModPlayer:
    """
    Class that should be inherited from for each unique Player.
    Every player currently starts with 1 card of each number.
    """   

    def start_game(self, identifier: int, player_count: int):
        self.identifier = identifier
        self.player_count = player_count
        self.hand = [str(i) for i in range(1, 11)]

    def take_turn(self, identifier: int, player_count: int):
        pass
    
    def observe_play(self, identifier: int, player_count: int, cards: str):
        pass

class ModController:
    RANKS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] #noqa
    RANK_STRENGTH = {rank: i for i, rank in enumerate(RANKS)} #noqa

    def __init__(self):
        self._players = []
    
    def join(self, player):
        if player not in self._players:
            self._players.append(player)

    def play_game(self):
        identity = 1
        evaluation = 0
        for player in self._players:
            player.start_game(identity, len(self._players))
            identity += 1

        cards_played = {
                    player.identifier: [] for player in self._players
                }
        while evaluation == 0 and len(self._players[0].hand) > 0:
            for player in self._players:
                card = player.take_turn(player.identifier, len(self._players))
                play = ModPlay(card, player.identifier)
                print(play)
                cards_played[player.identifier].append(play)
            for player in self._players:
                cards = [cards_played[p.identifier][-1] for p in self._players]
                player.observe_play(player.identifier, len(self._players), cards)
            card1 = int(cards_played[self._players[0].identifier][-1].rank)
            card2 = int(cards_played[self._players[1].identifier][-1].rank)
            evaluation = evaluate_round(card1, card2)
            print(f"Round evaluation: {evaluation}")
        if evaluation == 1:
            print(f"Player {self._players[0].identifier} wins!")
            return evaluation
        elif evaluation == 2:
            print(f"Player {self._players[1].identifier} wins!")
            return evaluation
        else:
            print("It's a tie!")
            return evaluation



def repeated_games(n: int, players: list):
    """
    Plays n games between two players and prints the results.
    """
    controller = ModController()
    results = []
    for player in players:
        controller.join(player)
    for i in range(n):
        print(f"Game {i + 1}:")
        result = controller.play_game()
        results.append(result)
        print("\n")
    counts = {1: results.count(1), 2: results.count(2), 0: results.count(0)}
    print(f"Player 1 wins: {counts[1]}")
    print(f"Player 2 wins: {counts[2]}")
    print(f"Ties: {counts[0]}")