"""Two-player Mod game engine.

Each player receives the numbers 1..m, plus three distinct duplicated numbers.
A game consists of m + 3 simultaneous-play rounds. A card wins a round if
it is exactly one higher than the opponent's card modulo m. The player with
more winning rounds wins the game.
"""

import random
from collections.abc import Sequence


class ModPlayer:
    """Base interface for agents playing the Mod game."""

    def __init__(self, name: str = "Player") -> None:
        self.name = name
        self.identifier = -1
        self.hand: list[int] = []

    def start_game(self, identifier: int, initial_hand: Sequence[int]) -> None:
        """Reset state at the start of every game."""
        self.identifier = identifier
        self.hand = list(initial_hand)

    def take_turn(self) -> int:
        """Choose a card from self.hand and remove it; override in subclasses."""
        raise NotImplementedError

    def observe_play(self, own_card: int, opponent_card: int, outcome: int) -> None:
        """Observe the round, with outcome 1 = win, 2 = loss, 0 = tie."""
        pass


class ModController:
    def __init__(self, m=10, extra_cards=0):
        self.m = m
        self.extra_cards = extra_cards
        self.rounds_per_game = m + extra_cards
        self._players = []

    def join(self, player):
        if player not in self._players:
            self._players.append(player)
    
    def _generate_hand(self) -> list[int]:
        """Return one of each number in 1..m, plus selected amount of distinct duplicates."""
        cards = list(range(1, self.m + 1))
        extra = random.sample(cards, self.extra_cards)
        hand = cards + extra
        random.shuffle(hand)
        return hand

    def _evaluate_round(self, card1: int, card2: int) -> int:
        """Return 1 if player 1 wins, 2 if player 2 wins, otherwise 0."""
        if (card1 - card2) % self.m == 1:
            return 1
        if (card2 - card1) % self.m == 1:
            return 2
        return 0

    def _take_card(self, player: ModPlayer, remaining: list[int]) -> int:
        """Validate a player's selection against the controller's hand."""
        card = player.take_turn()
        if card not in remaining:
            raise ValueError(f"{player.name} played an unavailable card: {card!r}")
        remaining.remove(card)
        return card

    def play(self, *, debug: bool = False) -> tuple[int, dict[int, int]]:
        """Play one game; return (winner, round scores).

        Player IDs are 1 and 2. Winner 0 means the game ended in a tie.
        """
        hands = [self._generate_hand(), self._generate_hand()]
        for identifier, (player, hand) in enumerate(zip(self._players, hands), start=1):
            player.start_game(identifier, hand)

        # These copies are authoritative: players cannot bypass card validation
        # by forgetting to remove a card from their own hand.
        remaining = [hand.copy() for hand in hands]
        scores = {1: 0, 2: 0}

        for round_number in range(1, self.rounds_per_game + 1):
            card1 = self._take_card(self._players[0], remaining[0])
            card2 = self._take_card(self._players[1], remaining[1])
            outcome = self._evaluate_round(card1, card2)
            if outcome:
                scores[outcome] += 1

            self._players[0].observe_play(card1, card2, outcome)
            # Convert outcomes to the second player's perspective.
            other_outcome = 3 - outcome if outcome else 0
            self._players[1].observe_play(card2, card1, other_outcome)

            if debug:
                print(f"Round {round_number}: P1={card1}, P2={card2}, winner={outcome}")

        winner = 1 if scores[1] > scores[2] else 2 if scores[2] > scores[1] else 0
        if debug:
            print(f"Final scores: {scores}; game winner: {winner}")
        return winner, scores

    def repeated_games(self, number_of_games: int, *, debug: bool = False) -> dict:
        """Run multiple games and return win counts and average round scores."""
        if number_of_games <= 0:
            raise ValueError("number_of_games must be positive")

        wins = {0: 0, 1: 0, 2: 0}
        total_round_scores = {1: 0, 2: 0}

        for game_number in range(1, number_of_games + 1):
            if debug:
                print(f"\n--- Game {game_number} ---")
            winner, scores = self.play(debug=debug)
            wins[winner] += 1
            for player_id in (1, 2):
                total_round_scores[player_id] += scores[player_id]

        return {
            "games": number_of_games,
            "wins": wins,
            "win_rates": {pid: count / number_of_games for pid, count in wins.items()},
            "average_round_scores": {
                pid: total / number_of_games
                for pid, total in total_round_scores.items()
            },
        }


