"""Monte Carlo second-order ToM, based on main/second_order_player.py."""

import random
from collections import Counter

from agents.second_order_player import SecondOrderPlayer


class SecondOrderMonteCarloPlayer(SecondOrderPlayer):
    def __init__(self, m=10, extra_cards=3, samples=100, name="ToM2 Monte Carlo"):
        super().__init__(m=m, extra_cards=extra_cards, name=name)
        if samples < 1:
            raise ValueError("samples must be positive")
        self.samples = samples

    def _predict_opponent_actions(self):
        # Sample possible ToM1 hands. Keep ToM1's inner prediction exact,
        # matching the original main-branch SecondOrderPlayer.
        possible_hands = self._possible_hands(self.opponent_history)
        tom0_actions = self._predict_tom0_actions(
            tom1_own_history=self.opponent_history,
            tom1_opponent_history=self.own_history,
        )

        actions = Counter()
        for _ in range(self.samples):
            hand = random.choice(possible_hands)
            predicted = self._predict_tom1_action(hand, tom0_actions)
            for card, probability in predicted.items():
                actions[card] += probability / self.samples

        return actions
