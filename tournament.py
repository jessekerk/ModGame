import itertools
import csv
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from modgame import ModController
from agents.random_player import RandomPlayer
from agents.zero_order_player import ZeroOrderPlayer
from agents.first_order_player import FirstOrderPlayer
from agents.second_order_player import SecondOrderPlayer
from agents.third_order_player import ThirdOrderPlayer
from agents.ToM1_MonteCarlo import FirstOrderMonteCarloPlayer
from agents.ToM2_MonteCarlo import SecondOrderMonteCarloPlayer
from agents.ToM3_MonteCarlo import ThirdOrderMonteCarloPlayer


class TournamentBenchmark:
    """Manages tournaments, metrics and CSV exports"""

    def __init__(self, agents, games_per_matchup=100, m=10, extra_cards=0, samples=100):
        self.agents = agents
        self.games_per_matchup = games_per_matchup
        self.m = m
        self.extra_cards = extra_cards
        self.results = []
        self.samples = samples

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
            matchup_start = time.perf_counter()

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

            # Record the runtime for this complete matchup (both playing sides).
            runtime_seconds = time.perf_counter() - matchup_start

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

            self._append_result(
                agent_a=agent_a.name,
                agent_b=agent_b.name,
                runtime_seconds=runtime_seconds,
                pairing_stats=pairing_stats,
            )

            self.results.append(pairing_stats)

    def _append_result(
        self, agent_a, agent_b, runtime_seconds, pairing_stats,
        output_dir="results"
    ):
        """Append runtime and matchup metrics to one CSV."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        runtime_file = output_path / "full_results.csv"

        columns = [
            "timestamp",
            "agent_a",
            "agent_b",
            "games",
            "m",
            "samples",
            "extra_cards",
            "runtime_seconds",
            "a_wins",
            "b_wins",
            "ties",
            "a_win_rate",
            "b_win_rate",
            "a_round_points",
            "b_round_points",
            "a_average_score",
            "b_average_score",
        ]

        write_header = (
            not runtime_file.exists() or runtime_file.stat().st_size == 0
        )

        with runtime_file.open("a", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=columns)

            if write_header:
                writer.writeheader()

            writer.writerow({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "agent_a": agent_a,
                "agent_b": agent_b,
                "games": self.games_per_matchup,
                "m": self.m,
                "extra_cards": self.extra_cards,
                "samples": self.samples,
                "runtime_seconds": round(runtime_seconds, 3),
                **{
                    key: pairing_stats[key]
                    for key in columns
                    if key in pairing_stats
                },
            })

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


def create_agents(agent_names, m, extra_cards, samples):
    agent_classes = {
        "Random": lambda: RandomPlayer(),
        "ZeroOrder": lambda: ZeroOrderPlayer(m=m, extra_cards=extra_cards),
        "FirstOrder": lambda: FirstOrderPlayer(m=m, extra_cards=extra_cards),
        "SecondOrder": lambda: SecondOrderPlayer(m=m, extra_cards=extra_cards),
        "ThirdOrder": lambda: ThirdOrderPlayer(m=m, extra_cards=extra_cards),
        "ToM1 Monte Carlo": lambda: FirstOrderMonteCarloPlayer(m=m, extra_cards=extra_cards, samples=samples),
        "ToM2 Monte Carlo": lambda: SecondOrderMonteCarloPlayer(m=m, extra_cards=extra_cards, samples=samples),
        "ToM3 Monte Carlo": lambda: ThirdOrderMonteCarloPlayer(m=m, extra_cards=extra_cards, samples=samples),
    }

    unknown = set(agent_names) - set(agent_classes)
    if unknown:
        raise ValueError(f"Unknown agents: {unknown}")

    return [agent_classes[name]() for name in agent_names]


def repeating_tournament(agent_names, extra_cards_list, samples_list, m, games_per_matchup):
    """
    If multiple extra cards or samples are selected, run multiple tournaments
    """
    if isinstance(extra_cards_list, int):
        extra_cards_list = [extra_cards_list]

    if isinstance(samples_list, int):
        samples_list = [samples_list]

    for extra_cards in extra_cards_list:
        for samples in samples_list:
            print("\n" + "=" * 60)
            print(f"Starting tournament: extra_cards={extra_cards}, samples={samples}")
            print("=" * 60)

            # Create agents for this configuration
            agent_list = create_agents(
                agent_names=agent_names,
                m=m,
                extra_cards=extra_cards,
                samples=samples,
            )

            # Setup tournament
            benchmark = TournamentBenchmark(
                agents=agent_list,
                games_per_matchup=games_per_matchup,
                m=m,
                extra_cards=extra_cards,
                samples=samples,
            )

            # Run tournament
            benchmark.run()
            benchmark.print_summary()


