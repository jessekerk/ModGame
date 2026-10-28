from tournament import repeating_tournament

# CONFIGURATION
# For EXTRA_CARDS and SAMPLES, you can use a list to make all combinations of tournaments.
# Integer also still works, so EXTRA_CARDS = 3 or EXTRA_CARDS = [0, 3] both work.
EXTRA_CARDS = 3
SAMPLES = 25
M = 10 # The amount of standard cards, which in our experiment is always [1, ..., 10]
GAMES_PER_MATCHUP = 1000

# SELECT AGENTS
AGENTS = [
    "Random",
    "ZeroOrder",
    "FirstOrder",
    "SecondOrder",
    "ThirdOrder",
    # "ToM1 Monte Carlo",
    # "ToM2 Monte Carlo",
    # "ToM3 Monte Carlo",
    "ToM1 MC Optimized",
    "ToM2 MC Optimized",
    "ToM3 MC Optimized"
]

if __name__ == "__main__":
    repeating_tournament(
        agent_names=AGENTS,
        extra_cards_list=EXTRA_CARDS,
        samples_list=SAMPLES,
        m=M,
        games_per_matchup=GAMES_PER_MATCHUP,
    )