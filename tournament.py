import itertools
from collections import defaultdict
from modgame import ModController
from random_player import RandomPlayer
from zero_order_player import ProbabilisticPlayer, DuplicateFirstPlayer
from first_order_player import FirstOrderPlayer
from second_order_player import SecondOrderPlayer



class TournamentBenchmark:
    """Manages tournaments and metrics"""

    def __init__(self, agents, games_per_matchup=100, m=10, extra_cards=0):
        self.agents = agents
        self.games_per_matchup = games_per_matchup
        self.m = m
        self.extra_cards = extra_cards
        self.results = []

    def _play_single_match(self, p1, p2):
        """Runs a single match"""

        controller = ModController(m=self.m, extra_cards=self.extra_cards)
        controller.join(p1)
        controller.join(p2)

        winner, scores = controller.play()

        # Return as tuple
        return winner, scores

    def run(self):
        """Runs all the matchup combinations"""

        matchups = list(itertools.combinations(self.agents, 2))
        print(f"Starting tournament: {len(self.agents)} agents, {len(matchups)} distinct pairings.")
        print(f"Games per pairing: {self.games_per_matchup}")

        half_games = self.games_per_matchup // 2

        for agent_a, agent_b in matchups:
            pairing_stats = {
                "agent_a": agent_a.name,
                "agent_b": agent_b.name,
                "a_wins": 0,
                "b_wins": 0,
                "ties": 0,
                "a_round_points": 0,
                "b_round_points": 0
            }

            # Series 1: Agent A as p1, Agent B as p2
            for _ in range(half_games):
                winner, scores = self._play_single_match(agent_a, agent_b)
                pairing_stats["a_round_points"] += scores[1]
                pairing_stats["b_round_points"] += scores[2]
                if winner == 1:
                    pairing_stats["a_wins"] += 1
                elif winner == 2:
                    pairing_stats["b_wins"] += 1
                else:
                    pairing_stats["ties"] += 1

            # Series 2: Swap sides (Agent B as p1, Agent A as p2)
            for _ in range(half_games):
                winner, scores = self._play_single_match(agent_b, agent_a)
                pairing_stats["b_round_points"] += scores[1]
                pairing_stats["a_round_points"] += scores[2]
                if winner == 1:
                    pairing_stats["b_wins"] += 1
                elif winner == 2:
                    pairing_stats["a_wins"] += 1
                else:
                    pairing_stats["ties"] += 1

            self.results.append(pairing_stats)

    def print_summary(self) -> None:
        """Prints a readable summary of tournament results."""
        print("\n=== MATCHUP RESULTS ===")
        for res in self.results:
            agent_a = res["agent_a"]
            agent_b = res["agent_b"]
            win_rate = (res["a_wins"] / self.games_per_matchup) * 100

            print(f"{agent_a} vs {agent_b}:")
            print(f"  Score: {agent_a} won {res['a_wins']}, {agent_b} won {res['b_wins']} (Ties: {res['ties']})")
            print(f"  {agent_a} Win Rate: {round(win_rate, 1)}%")
            print(f"  Average Points: {agent_a} = {round(res['a_round_points'] / self.games_per_matchup, 2)}, "
                  f"{agent_b} = {round(res['b_round_points'] / self.games_per_matchup, 2)}")
            print("-" * 40)

        # Count total wins across all matches
        total_wins = defaultdict(int)
        for res in self.results:
            total_wins[res["agent_a"]] += res["a_wins"]
            total_wins[res["agent_b"]] += res["b_wins"]

        print("\n=== TOTAL WINS ===")
        for agent_name, wins in total_wins.items():
            print(f"{agent_name}: {wins} total wins")


if __name__ == "__main__":

    EXTRA_CARDS = 0

    agent_list = [
        RandomPlayer(name="Random"),
        DuplicateFirstPlayer(name="DuplicateFirst"),
        ProbabilisticPlayer(name="Probabilistic", extra_cards=EXTRA_CARDS),
        FirstOrderPlayer(m=10, extra_cards=EXTRA_CARDS),
        SecondOrderPlayer(m=10, extra_cards=EXTRA_CARDS)
    ]

    benchmark = TournamentBenchmark(
        agents=agent_list,
        games_per_matchup=1000,
        m=10,
        extra_cards=EXTRA_CARDS
    )

    benchmark.run()
    benchmark.print_summary()