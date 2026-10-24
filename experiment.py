"""Compare original ToM0 with Monte Carlo ToM1 and ToM2.

Uses the existing main-branch ModController with three distinct duplicates.
"""

import random

from modgame import ModController
from zero_order_player import ProbabilisticPlayer
from ToM1_MonteCarlo import FirstOrderMonteCarloPlayer
from ToM2_MonteCarlo import SecondOrderMonteCarloPlayer


def main():
    m = 10
    extra_cards = 3
    samples = 100
    games_per_matchup = 1000  # Even: equal games in both player positions.
    random.seed(42)

    models = [
        ("ToM0", lambda: ProbabilisticPlayer(m=m, extra_cards=extra_cards)),
        (
            "ToM1 MC",
            lambda: FirstOrderMonteCarloPlayer(
                m=m, extra_cards=extra_cards, samples=samples
            ),
        ),
        (
            "ToM2 MC",
            lambda: SecondOrderMonteCarloPlayer(
                m=m, extra_cards=extra_cards, samples=samples
            ),
        ),
    ]

    for i, (name_a, make_a) in enumerate(models):
        for name_b, make_b in models[i + 1 :]:
            a_wins = b_wins = ties = 0

            for game in range(games_per_matchup):
                swapped = game % 2 == 1
                controller = ModController(m=m, extra_cards=extra_cards)
                agent_a, agent_b = make_a(), make_b()
                controller.join(agent_b if swapped else agent_a)
                controller.join(agent_a if swapped else agent_b)

                winner, _ = controller.play()
                if winner == 0:
                    ties += 1
                elif (winner == 1 and not swapped) or (winner == 2 and swapped):
                    a_wins += 1
                else:
                    b_wins += 1

            print(f"\n{name_a} vs {name_b} ({games_per_matchup} games)")
            print(f"  {name_a}: {a_wins / games_per_matchup:.1%}")
            print(f"  {name_b}: {b_wins / games_per_matchup:.1%}")
            print(f"  Ties: {ties / games_per_matchup:.1%}")


if __name__ == "__main__":
    main()
