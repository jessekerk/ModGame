import random  # noqa: F401
from typing import List



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

def generate_hand():
    """Generates a 13-card hand: 1-10 plus 3 randomly duplicated cards."""
    base_cards = list(range(1, 11))
    duplicates = random.sample(base_cards, 3)
    hand = base_cards + duplicates
    random.shuffle(hand)
    return hand

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

    def __init__(self, name: str = "Player") -> None:
        self.name = name
        self.identifier = -1
        self.hand = []

    def start_game(self, identifier: int, player_count: int, initial_hand: List[int]):
        self.identifier = identifier
        self.player_count = player_count
        self.hand = initial_hand.copy()

    def take_turn(self, identifier: int, player_count: int):
        pass
    
    def observe_play(self, identifier: int, player_count: int, cards: str):
        pass

class ModController:
    RANKS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] #noqa
    RANK_STRENGTH = {rank: i for i, rank in enumerate(RANKS)} #noqa

    def __init__(self, player1: ModPlayer, player2: ModPlayer) -> None:
        self.players = [player1, player2]

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

    def play_game_2(self, verbose: bool = False):
        """Executes a full 13-round game.

        Returns:
            Tuple of (overall_winner, final_scores) where overall_winner is
            1, 2, or 0 (tie).
        """
        # Assign unique random 13-card hands
        p1_hand = generate_hand()
        p2_hand = generate_hand()
        self.players[0].start_game(1, p1_hand)
        self.players[1].start_game(2, p2_hand)

        scores = {1: 0, 2: 0}

        for round_nr in range(1, 14):
            card1 = self.players[0].take_turn()
            card2 = self.players[1].take_turn()

            outcome = evaluate_round(card1, card2)
            if outcome == 1:
                scores[1] += 1
            elif outcome == 2:
                scores[2] += 1

            self.players[0].observe_play(card1, card2, outcome)
            self.players[1].observe_play(card2, card1, outcome)

            if verbose:
                print(f"Round {round_nr}: P1 played {card1}, P2 played {card2} -> Winner: {outcome}")

        if scores[1] > scores[2]:
            winner = 1
        elif scores[2] > scores[1]:
            winner = 2
        else:
            winner = 0

        return winner, scores


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



def repeated_games_2(n: int, player1: ModPlayer, player2: ModPlayer, verbose: bool = False) -> None:
    """
    Plays n games between two players and prints the results.
    """
    controller = ModController(player1, player2)
    win_counts = {1: 0, 2: 0, 0: 0}
    total_scores = {1: 0, 2: 0}

    for _ in range(n):
        winner, scores = controller.play_game_2(verbose=verbose)
        win_counts[winner] += 1
        total_scores[1] += scores[1]
        total_scores[2] += scores[2]

    print(f"--- Results after {n} games ---")
    print(f"{player1.name} (P1) Wins: {win_counts[1]} ({win_counts[1] / n * 100:.1f}%)")
    print(f"{player2.name} (P2) Wins: {win_counts[2]} ({win_counts[2] / n * 100:.1f}%)")
    print(f"Ties: {win_counts[0]} ({win_counts[0] / n * 100:.1f}%)")
    print(f"Average Round Score: P1 = {total_scores[1] / n:.2f} | P2 = {total_scores[2] / n:.2f}")