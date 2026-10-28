"""ToM2 Monte Carlo agent using direct valid-hand sampling at each sampled level."""
from agents.second_order_player import SecondOrderPlayer
from agents.monte_carlo_sampling_utils import estimate_remaining_cards, sample_remaining_hand


class SecondOrderMonteCarloOptimizedPlayer(SecondOrderPlayer):
    def __init__(self, m=10, extra_cards=3, samples=100, name="ToM2 MC Optimized"):
        super().__init__(m=m, extra_cards=extra_cards, name=name)
        if samples < 1:
            raise ValueError("samples must be positive")
        self.samples = samples

    def _estimate_remaining_cards(self, played_history):
        return estimate_remaining_cards(played_history, self.m, self.extra_cards)

    def _possible_hands(self, played_history):
        return [
            sample_remaining_hand(played_history, self.m, self.extra_cards)
            for _ in range(self.samples)
        ]
