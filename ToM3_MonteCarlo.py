
"""Monte Carlo third-order ToM, based on third_order_player.py."""

import random
from collections import Counter

from third_order_player import ThirdOrderPlayer


class ThirdOrderMonteCarloPlayer(ThirdOrderPlayer):
    def __init__(self, m=10, extra_cards=3, samples=100, name="ToM3 Monte Carlo"):
        super().__init__(m=m, extra_cards=extra_cards, name=name)

        if samples < 1:
            raise ValueError("samples must be positive")

        self.samples = samples

    def _predict_opponent_actions(self):
        # Keep ToM0's prediction exact.
        tom0_actions = self._predict_tom0_actions(tom1_own_history=self.own_history, tom1_opponent_history=self.opponent_history)

        # Calculate ToM1's predicted actions, as ToM2 would.
        possible_tom1_hands = self._possible_hands(self.own_history)

        tom1_actions = Counter()

        for tom1_hand in possible_tom1_hands:
            predicted = self._predict_tom1_action(tom1_hand=tom1_hand, tom0_actions=tom0_actions)

            for card, probability in predicted.items():
                tom1_actions[card] += (probability / len(possible_tom1_hands))

        # Sample possible ToM2 hands instead of evaluating
        # every possible ToM2 hand.
        possible_tom2_hands = self._possible_hands(self.opponent_history)

        actions = Counter()

        for _ in range(self.samples):
            hand = random.choice(possible_tom2_hands)

            predicted = self._predict_tom1_action(tom1_hand=hand, tom0_actions=tom1_actions)

            for card, probability in predicted.items():
                actions[card] += probability / self.samples

        return actions
