import random
from collections import Counter

from modgame import ModPlayer


class DuplicateFirstPlayer(ModPlayer):
    """
    Zero-order agent that plays duplicate cards first.

    The strategy preserves as many different card values
    as possible for later rounds.
    """

    def __init__(self, name: str = "Duplicate First"):
        super().__init__(name)

    def take_turn(self) -> int:
        counts = Counter(self.hand)

        # Find cards that appear more than once
        duplicates = [card for card in self.hand if counts[card] > 1]

        if duplicates:
            card = random.choice(duplicates)
        else:
            card = random.choice(self.hand)

        self.hand.remove(card)
        return card


class ProbabilisticPlayer(ModPlayer):
    """
    Zero-order agent that maximizes the estimated probability
    of winning the current round.

    Assumes the opponent chooses uniformly at random from
    their remaining cards.
    """

    def __init__(self, m: int = 10, name: str = "Probabilistic ToM0"):
        super().__init__(name)
        self.m = m
        self.opponent_history = []

    def start_game(self, identifier, initial_hand):
        super().start_game(identifier, initial_hand)
        self.opponent_history = []

    def observe_play(self, own_card, opponent_card, outcome):
        self.opponent_history.append(opponent_card)

    def _estimate_opponent_cards(self):
        """
        Estimate remaining opponent card frequencies.

        Each player initially has one of every card, plus
        three distinct randomly duplicated cards.

        The opponent's exact duplicates are unknown.
        """
        played = Counter(self.opponent_history)

        estimates = {}

        for card in range(1, self.m + 1):
            # One guaranteed copy, plus the expected
            # contribution from the three duplicates
            expected_initial = 1 + 3 / self.m

            estimates[card] = max(0, expected_initial - played[card])

        return estimates

    def take_turn(self) -> int:
        estimates = self._estimate_opponent_cards()

        best_cards = []
        best_probability = -1

        total = sum(estimates.values())

        for card in set(self.hand):
            # Card that this card defeats
            target = (card - 2) % self.m + 1

            probability = estimates[target] / total if total > 0 else 0

            if probability > best_probability:
                best_probability = probability
                best_cards = [card]

            elif probability == best_probability:
                best_cards.append(card)

        card = random.choice(best_cards)
        self.hand.remove(card)
        return card
