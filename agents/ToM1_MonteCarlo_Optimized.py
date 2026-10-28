"""ToM1 Monte Carlo agent using direct valid-hand sampling."""
from collections import Counter
from agents.first_order_player import FirstOrderPlayer
from agents.monte_carlo_sampling_utils import estimate_remaining_cards, sample_remaining_hand


class FirstOrderMonteCarloOptimizedPlayer(FirstOrderPlayer):
    def __init__(self, m=10, extra_cards=3, samples=100, name="ToM1 MC Optimized"):
        super().__init__(m=m, extra_cards=extra_cards, name=name)
        if samples < 1:
            raise ValueError("samples must be positive")
        self.samples = samples

    def _estimate_my_remaining_cards(self):
        return estimate_remaining_cards(self.own_history, self.m, self.extra_cards)

    def _predict_opponent_actions(self):
        estimates = self._estimate_my_remaining_cards()
        total = sum(estimates.values())
        actions = Counter()
        for _ in range(self.samples):
            hand = sample_remaining_hand(self.opponent_history, self.m, self.extra_cards)
            available = [card for card, count in hand.items() if count > 0]
            if not available:
                continue
            scores = {
                card: estimates[(card - 2) % self.m + 1] / total if total else 0
                for card in available
            }
            best = max(scores.values())
            best_cards = [card for card in available if scores[card] == best]
            for card in best_cards:
                actions[card] += 1 / (self.samples * len(best_cards))
        return actions
