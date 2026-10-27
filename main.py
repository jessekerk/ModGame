from tournament import repeating_tournament

# CONFIGURATION
# For EXTRA_CARDS and SAMPLES, you can use a list to make all combinations of tournaments.
# Integer also still works, so EXTRA_CARDS = 3 or EXTRA_CARDS = [0, 3] both work.
EXTRA_CARDS = [0, 3]
SAMPLES = [5, 25, 50, 100]
M = 10
GAMES_PER_MATCHUP = 1000

# SELECT AGENTS
AGENTS = [
    "Random",
    "ZeroOrder",
    "FirstOrder",
    "SecondOrder",
    "ThirdOrder",
    "ToM1 Monte Carlo",
    "ToM2 Monte Carlo",
    "ToM3 Monte Carlo",
]

if __name__ == "__main__":
    repeating_tournament(
        agent_names=AGENTS,
        extra_cards_list=EXTRA_CARDS,
        samples_list=SAMPLES,
        m=M,
        games_per_matchup=GAMES_PER_MATCHUP,
    )