import random
from collections import Counter
from itertools import combinations

from modgame import ModPlayer


class SecondOrderPlayer(ModPlayer):
    """
    Second-order Theory of Mind agent.

    Assumes the opponent uses FirstOrderPlayer (ToM1).
    Simulates ToM1's decision rule for possible opponent
    hands, then chooses the card with the highest
    predicted probability of winning the current round.
    """

    def __init__(self, m: int = 10, extra_cards: int = 0, name: str = "SecondOrderPlayer"):
        super().__init__(name)
        self.m = m
        self.extra_cards = extra_cards
        self.own_history = []
        self.opponent_history = []

    def start_game(self, identifier, initial_hand):
        super().start_game(identifier, initial_hand)
        self.own_history = []
        self.opponent_history = []

    def observe_play(self, own_card, opponent_card, outcome):
        self.own_history.append(own_card)
        self.opponent_history.append(opponent_card)

    def _estimate_remaining_cards(self, played_history):
        """
        Expected remaining card frequencies under ToM0's
        model: one copy of each card plus the expected
        contribution from extra cards.
        """
        played = Counter(played_history)
        estimates = {}

        for card in range(1, self.m + 1):
            expected_initial = 1 + self.extra_cards / self.m
            estimates[card] = max(0, expected_initial - played[card])

        return estimates

    def _possible_hands(self, played_history):
        """
        Enumerate possible remaining hands consistent
        with the observed played cards.
        """
        played = Counter(played_history)
        possible_hands = []

        for duplicates in combinations(range(1, self.m + 1), self.extra_cards):
            duplicate_set = set(duplicates)
            remaining = {}
            valid = True

            for card in range(1, self.m + 1):
                initial_count = 1 + (card in duplicate_set)

                if played[card] > initial_count:
                    valid = False
                    break

                remaining[card] = initial_count - played[card]

            if valid:
                possible_hands.append(remaining)

        if not possible_hands:
            raise ValueError("No possible hand matches the observed plays.")

        return possible_hands

    def _predict_tom0_actions(self, tom1_own_history, tom1_opponent_history):
        """
        Reproduce the opponent-action prediction used
        by the existing FirstOrderPlayer.
        """
        estimates = self._estimate_remaining_cards(tom1_own_history)
        total = sum(estimates.values())

        possible_hands = self._possible_hands(tom1_opponent_history)

        action_probabilities = Counter()

        for hand in possible_hands:
            available_cards = [card for card, count in hand.items() if count > 0]

            if not available_cards:
                continue

            card_scores = {}

            for card in available_cards:
                target = (card - 2) % self.m + 1

                card_scores[card] = (estimates[target] / total if total > 0 else 0)

            best_score = max(card_scores.values())
            best_cards = [card for card, score in card_scores.items() if score == best_score]

            for card in best_cards:
                action_probabilities[card] += (1 / len(possible_hands) / len(best_cards))

        return action_probabilities

    def _predict_tom1_action(self, tom1_hand, tom1_own_history, tom1_opponent_history):
        """
        Simulate one possible FirstOrderPlayer.

        Its own history contains cards played by ToM1;
        its opponent history contains cards played by ToM2.
        """
        tom0_actions = self._predict_tom0_actions(tom1_own_history, tom1_opponent_history)

        best_cards = []
        best_probability = -1

        for card, count in tom1_hand.items():
            if count <= 0:
                continue

            probability = sum(
                opponent_probability
                for opponent_card, opponent_probability
                in tom0_actions.items()
                if (card - opponent_card) % self.m == 1
            )

            if probability > best_probability:
                best_probability = probability
                best_cards = [card]

            elif probability == best_probability:
                best_cards.append(card)

        # FirstOrderPlayer randomly breaks ties.
        action_probabilities = Counter()

        if best_cards:
            for card in best_cards:
                action_probabilities[card] = 1 / len(best_cards)

        return action_probabilities

    def _predict_opponent_actions(self):
        """
        Predict ToM1's next card by averaging its
        decision rule across possible remaining hands.
        """
        possible_tom1_hands = self._possible_hands(self.opponent_history)

        action_probabilities = Counter()
        number_of_hands = len(possible_tom1_hands)

        for tom1_hand in possible_tom1_hands:
            tom1_actions = self._predict_tom1_action(
                tom1_hand=tom1_hand,
                # ToM1's own cards played are the cards
                # ToM2 observed ToM1 play.
                tom1_own_history=self.opponent_history,
                # ToM1's opponent history is ToM2's
                # previously played cards.
                tom1_opponent_history=self.own_history,
            )

            for card, probability in tom1_actions.items():
                action_probabilities[card] += (probability / number_of_hands)

        return action_probabilities

    def take_turn(self) -> int:
        """
        Choose the card with the highest predicted
        probability of winning against ToM1.
        """
        opponent_actions = self._predict_opponent_actions()

        best_cards = []
        best_probability = -1

        for card in set(self.hand):
            probability = sum(
                opponent_probability
                for opponent_card, opponent_probability
                in opponent_actions.items()
                if (card - opponent_card) % self.m == 1
            )

            if probability > best_probability:
                best_probability = probability
                best_cards = [card]

            elif probability == best_probability:
                best_cards.append(card)

        card = random.choice(best_cards)
        self.hand.remove(card)

        return card
