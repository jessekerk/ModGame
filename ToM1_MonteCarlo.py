"""Monte Carlo first-order ToM, based on main/first_order_player.py."""

import random
from collections import Counter

from first_order_player import FirstOrderPlayer


class FirstOrderMonteCarloPlayer(FirstOrderPlayer):
    def __init__(self, m=10, extra_cards=3, samples=100, name="ToM1 Monte Carlo"):
        super().__init__(m=m, extra_cards=extra_cards, name=name)
        if samples < 1:
            raise ValueError("samples must be positive")
        self.samples = samples

    def _predict_opponent_actions(self):
        # Model the opponent as the original ProbabilisticPlayer (ToM0).
        estimates = self._estimate_my_remaining_cards()
        total = sum(estimates.values())
        possible_hands = self._possible_opponent_hands()

        actions = Counter()
        for _ in range(self.samples):
            hand = random.choice(possible_hands)
            available = [card for card, count in hand.items() if count > 0]

            scores = {
                card: estimates[(card - 2) % self.m + 1] / total if total else 0
                for card in available
            }
            best = max(scores.values())
            best_cards = [card for card in available if scores[card] == best]

            for card in best_cards:
                actions[card] += 1 / (self.samples * len(best_cards))

        return actions
