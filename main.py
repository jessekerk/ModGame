from modgame import ModController
from agents.random_player import RandomPlayer
from agents.zero_order_player import ZeroOrderPlayer
from agents.first_order_player import FirstOrderPlayer
from agents.second_order_player import SecondOrderPlayer
from agents.third_order_player import ThirdOrderPlayer
from agents.ToM1_MonteCarlo import FirstOrderMonteCarloPlayer
from agents.ToM2_MonteCarlo import SecondOrderMonteCarloPlayer
from agents.ToM3_MonteCarlo import ThirdOrderMonteCarloPlayer
from tournament import TournamentBenchmark



if __name__ == "__main__":

    # CONFIGURATION
    EXTRA_CARDS = 3
    M = 10
    GAMES_PER_MATCHUP = 10
    SAMPLES = 100

    # CHOOSING SELECTED AGENTS
    agent_list = [
        RandomPlayer(),
        ZeroOrderPlayer(m=M, extra_cards=EXTRA_CARDS),
        FirstOrderPlayer(m=M, extra_cards=EXTRA_CARDS),
        SecondOrderPlayer(m=M, extra_cards=EXTRA_CARDS),
        ThirdOrderPlayer(m=M, extra_cards=EXTRA_CARDS),
        FirstOrderMonteCarloPlayer(
            m=M, extra_cards=EXTRA_CARDS, samples=SAMPLES,
            name="ToM1 Monte Carlo"
        ),
        SecondOrderMonteCarloPlayer(
            m=M, extra_cards=EXTRA_CARDS, samples=SAMPLES,
            name="ToM2 Monte Carlo"
        ),
        ThirdOrderMonteCarloPlayer(
            m=M, extra_cards=EXTRA_CARDS, samples=SAMPLES,
            name="ToM3 Monte Carlo"
        )
    ]

    # SETUP TOURNAMENT
    benchmark = TournamentBenchmark(
        agents=agent_list,
        games_per_matchup=GAMES_PER_MATCHUP,
        m=M,
        extra_cards=EXTRA_CARDS,
        samples=SAMPLES,
    )

    # RUN TOURNAMENT
    benchmark.run()
    benchmark.print_summary()