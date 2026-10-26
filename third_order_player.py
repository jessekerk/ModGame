
import random
from collections import Counter

from second_order_player import SecondOrderPlayer


class ThirdOrderPlayer(SecondOrderPlayer):
    """
    Third-order Theory of Mind agent (ToM3).

    Assumes the opponent uses SecondOrderPlayer (ToM2).
    Simulates ToM2's decision rule for possible opponent
    hands, then chooses the card with the highest
    predicted probability of winning the current round.
    """

    def __init__(self, m: int = 10, extra_cards: int = 0, name: str = "ThirdOrderPlayer"):
        super().__init__(m=m, extra_cards=extra_cards, name=name)

    def _predict_opponent_actions(self):
        """
        Predict ToM2's next card by simulating its
        decision rule across possible remaining hands.
        """

        # Simulate ToM2's prediction of ToM0.
        tom0_actions = self._predict_tom0_actions(tom1_own_history=self.own_history, tom1_opponent_history=self.opponent_history)

        # Predict ToM1's actions, as ToM2 would.
        possible_tom1_hands = self._possible_hands(self.own_history)

        tom1_actions = Counter()
        for tom1_hand in possible_tom1_hands:
            actions = self._predict_tom1_action(tom1_hand=tom1_hand, tom0_actions=tom0_actions,)

            for card, probability in actions.items():
                tom1_actions[card] += (probability / len(possible_tom1_hands))

        # Simulate ToM2 choosing its card against ToM1.
        possible_tom2_hands = self._possible_hands(self.opponent_history)

        tom2_actions = Counter()
        for tom2_hand in possible_tom2_hands:
            actions = self._predict_tom1_action(tom1_hand=tom2_hand, tom0_actions=tom1_actions)

            for card, probability in actions.items():
                tom2_actions[card] += (probability / len(possible_tom2_hands))

        return tom2_actions
