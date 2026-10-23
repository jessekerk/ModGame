import itertools
import csv
from pathlib import Path
from collections import defaultdict
from modgame import ModController
from random_player import RandomPlayer
from zero_order_player import ProbabilisticPlayer, DuplicateFirstPlayer
from first_order_player import FirstOrderPlayer
from second_order_player import SecondOrderPlayer



class TournamentBenchmark:
    """Manages tournaments, metrics and CSV exports"""

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

                        # Calculate metrics
            games = self.games_per_matchup

            pairing_stats["a_win_rate"] = (
                pairing_stats["a_wins"] / games * 100 if games else 0
            )
            pairing_stats["b_win_rate"] = (
                pairing_stats["b_wins"] / games * 100 if games else 0
            )
            pairing_stats["a_average_score"] = (
                pairing_stats["a_round_points"] / games if games else 0
            )
            pairing_stats["b_average_score"] = (
                pairing_stats["b_round_points"] / games if games else 0
            )

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

    def export_csv(self, output_dir="tournament_results"):
        """Exports detailed results and two comparison matrices."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 1. Detailed matchup results
        details_file = output_path / "matchup_results.csv"

        columns = [
            "agent_a",
            "agent_b",
            "m",
            "extra_cards",
            "games",
            "a_wins",
            "b_wins",
            "ties",
            "a_win_rate",
            "b_win_rate",
            "a_average_score",
            "b_average_score",
            "a_round_points",
            "b_round_points",
        ]

        with details_file.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()

            for res in self.results:
                row = {
                    **res,
                    "m": self.m,
                    "extra_cards": self.extra_cards,
                    "games": self.games_per_matchup,
                }
                writer.writerow({key: row[key] for key in columns})

        # 2. Win-rate matrix
        agent_names = [agent.name for agent in self.agents]
        win_matrix = {name: {opponent: "" for opponent in agent_names}
                      for name in agent_names}
        score_matrix = {name: {opponent: "" for opponent in agent_names}
                        for name in agent_names}

        for res in self.results:
            a = res["agent_a"]
            b = res["agent_b"]

            # Row = agent, column = opponent
            win_matrix[a][b] = round(res["a_win_rate"], 2)
            win_matrix[b][a] = round(res["b_win_rate"], 2)

            score_matrix[a][b] = round(res["a_average_score"], 3)
            score_matrix[b][a] = round(res["b_average_score"], 3)

        win_file = output_path / "win_rate_matrix.csv"
        with win_file.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Agent vs opponent (%)"] + agent_names)

            for name in agent_names:
                writer.writerow(
                    [name] + [win_matrix[name][opponent]
                              for opponent in agent_names]
                )

        score_file = output_path / "average_score_matrix.csv"
        with score_file.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Agent vs opponent (points/game)"] + agent_names)

            for name in agent_names:
                writer.writerow(
                    [name] + [score_matrix[name][opponent]
                              for opponent in agent_names]
                )

        print("\n=== CSV EXPORT ===")
        print(f"Detailed results: {details_file}")
        print(f"Win-rate matrix: {win_file}")
        print(f"Average-score matrix: {score_file}")


if __name__ == "__main__":

    EXTRA_CARDS = 0
    M = 10
    GAMES_PER_MATCHUP = 100

    agent_list = [
        RandomPlayer(name="Random"),
        DuplicateFirstPlayer(name="DuplicateFirst"),
        ProbabilisticPlayer(name="Probabilistic", m=M, extra_cards=EXTRA_CARDS),
        FirstOrderPlayer(m=M, extra_cards=EXTRA_CARDS),
        SecondOrderPlayer(m=M, extra_cards=EXTRA_CARDS)
    ]

    benchmark = TournamentBenchmark(
        agents=agent_list,
        games_per_matchup=GAMES_PER_MATCHUP,
        m=M,
        extra_cards=EXTRA_CARDS
    )

    benchmark.run()
    benchmark.print_summary()
    benchmark.export_csv()