import random
from collections import Counter
from itertools import combinations

from modgame import ModPlayer


class FirstOrderPlayer(ModPlayer):
    """
    First-order Theory of Mind agent.

    Assumes the opponent uses ProbabilisticPlayer (ToM0).
    Enumerates possible opponent hands and predicts which
    card the opponent is likely to play.
    """

    def __init__(
        self,
        m: int = 10,
        extra_cards: int = 0,
        name: str = "FirstOrderPlayer",
    ):
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

    def _estimate_my_remaining_cards(self):
        """
        Estimate the cards that the opponent believes
        I still have, using the updated ToM0 model.

        Enumerate compatible duplicate configurations
        based on my publicly observed previous plays.
        """
        played = Counter(self.own_history)
        possible_hands = []

        for duplicates in combinations(range(1, self.m + 1), self.extra_cards):
            duplicate_set = set(duplicates)
            remaining = {}

            for card in range(1, self.m + 1):
                initial = 1 + (card in duplicate_set)
                remaining[card] = initial - played[card]

            if all(count >= 0 for count in remaining.values()):
                possible_hands.append(remaining)

        if not possible_hands:
            raise ValueError("No possible hand matches my observed plays.")

        estimates = {
            card: sum(hand[card] for hand in possible_hands) / len(possible_hands)
            for card in range(1, self.m + 1)
        }

        return estimates

    def _possible_opponent_hands(self):
        """
        Enumerate possible sets of duplicated cards.

        Remove cards already played by the opponent and
        discard duplicate sets that cannot explain the
        observed plays.
        """
        played = Counter(self.opponent_history)

        duplicate_sets = combinations(range(1, self.m + 1), self.extra_cards)

        possible_hands = []

        for duplicates in duplicate_sets:
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
            raise ValueError("No possible opponent hand matches the observed plays.")

        return possible_hands

    def _predict_opponent_actions(self):
        """
        Predict the opponent's card distribution.

        For each possible opponent hand, simulate the
        decision rule used by the updated ProbabilisticPlayer.
        """
        estimates = self._estimate_my_remaining_cards()
        total = sum(estimates.values())

        possible_hands = self._possible_opponent_hands()
        action_probabilities = Counter()

        for hand in possible_hands:
            available_cards = [card for card, count in hand.items() if count > 0]

            if not available_cards:
                continue

            card_scores = {}

            for card in available_cards:
                target = (card - 2) % self.m + 1

                probability = estimates[target] / total if total > 0 else 0

                card_scores[card] = probability

            best_score = max(card_scores.values())

            best_cards = [
                card for card, score in card_scores.items() if score == best_score
            ]

            # ProbabilisticPlayer randomly chooses among
            # cards with the same best score.
            for card in best_cards:
                action_probabilities[card] += 1 / len(possible_hands) / len(best_cards)

        return action_probabilities

    def take_turn(self) -> int:
        """
        Choose the card with the highest predicted
        probability of winning the current round.
        """
        opponent_actions = self._predict_opponent_actions()

        best_cards = []
        best_probability = -1

        for card in set(self.hand):
            probability = sum(
                opponent_probability
                for opponent_card, opponent_probability in opponent_actions.items()
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
