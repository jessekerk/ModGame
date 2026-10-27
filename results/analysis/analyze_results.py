
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "results" / "full_results.csv"
OUTPUT_ROOT = PROJECT_ROOT / "results" / "analysis"

# Different experiments will receive separate output folders.
CONFIG_COLUMNS = ["extra_cards", "samples", "games_setting", "m"]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def normalize_setting(value, default="unknown"):
    """Convert settings to consistent labels, e.g. 100.0 -> '100'."""
    if pd.isna(value):
        return default

    if isinstance(value, (int, float, np.integer, np.floating)):
        if float(value).is_integer():
            return str(int(value))

    return str(value).strip()


def plot_heatmap(matrix, title, output_file, metric):
    """Create and save an annotated heatmap."""

    number_of_agents = len(matrix)

    fig, ax = plt.subplots(
        figsize=(
            max(8, number_of_agents * 1.1),
            max(6, number_of_agents * 0.9),
        )
    )

    # Display missing values, such as the diagonal, in grey.
    masked_matrix = np.ma.masked_invalid(matrix.to_numpy(dtype=float))
    ax.set_facecolor("#eeeeee")

    if metric == "win_rate":
        color_map = "RdYlGn"
        vmin, vmax = 0, 1
    else:
        color_map = "viridis"
        vmin = vmax = None

    image = ax.imshow(
        masked_matrix,
        cmap=color_map,
        vmin=vmin,
        vmax=vmax,
        aspect="auto",
    )

    colorbar = fig.colorbar(image, ax=ax, shrink=0.85)

    if metric == "win_rate":
        colorbar.set_label("Win rate")
    else:
        colorbar.set_label("Average score per game")

    ax.set_xticks(range(number_of_agents))
    ax.set_yticks(range(number_of_agents))

    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticklabels(matrix.index)

    ax.set_xlabel("Opponent")
    ax.set_ylabel("Agent")
    ax.set_title(title, pad=16)

    # Write the numerical value inside each cell.
    values = matrix.to_numpy(dtype=float)

    for row in range(number_of_agents):
        for col in range(number_of_agents):
            value = values[row, col]

            if np.isfinite(value):
                if metric == "win_rate":
                    label = f"{value:.1%}"
                else:
                    label = f"{value:.2f}"

                ax.text(
                    col,
                    row,
                    label,
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="black",
                )

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------
# LOAD AND VALIDATE DATA
# --------------------------------------------------

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Results file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    required_columns = [
        "agent_a",
        "agent_b",
        "games",
        "extra_cards",
        "m",
        "a_wins",
        "b_wins",
        "a_average_score",
        "b_average_score",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns in full_results.csv: {missing}"
        )

    if df.empty:
        print("The results file is empty.")
        return

    # Older CSV files may not contain a samples column.
    # Such results are labelled 'unknown', never guessed.
    if "samples" not in df.columns:
        df["samples"] = "unknown"

    # Standardize configuration labels.
    for col in ["extra_cards", "samples", "games", "m"]:
        df[col] = df[col].apply(normalize_setting)

    # The games column is a configuration setting.
    df = df.rename(columns={"games": "games_setting"})

    # Convert numerical columns.
    numeric_columns = [
        "games_setting",
        "a_wins",
        "b_wins",
        "a_average_score",
        "b_average_score",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=[
            "games_setting",
            "a_wins",
            "b_wins",
            "a_average_score",
            "b_average_score",
        ]
    )

    df = df[df["games_setting"] > 0].copy()

    if df.empty:
        print("No valid matchup results found.")
        return

    # --------------------------------------------------
    # STANDARDIZE MATCHUP ORIENTATION
    # --------------------------------------------------
    # If a matchup appears as B vs A in one run and A vs B
    # in another, swap the corresponding metrics so that
    # repeated results can be aggregated consistently.

    reverse = df["agent_a"] > df["agent_b"]

    for col_a, col_b in [
        ("agent_a", "agent_b"),
        ("a_wins", "b_wins"),
        ("a_average_score", "b_average_score"),
    ]:
        original_a = df.loc[reverse, col_a].copy()
        df.loc[reverse, col_a] = df.loc[reverse, col_b].to_numpy()
        df.loc[reverse, col_b] = original_a.to_numpy()

    # Score totals allow results from repeated runs to be
    # weighted by the number of games, rather than averaging
    # matchup averages equally.
    df["_games_count"] = df["games_setting"]
    df["_a_score_total"] = (
        df["a_average_score"] * df["_games_count"]
    )
    df["_b_score_total"] = (
        df["b_average_score"] * df["_games_count"]
    )

    # --------------------------------------------------
    # GROUP BY EXPERIMENT CONFIGURATION
    # --------------------------------------------------

    configuration_groups = df.groupby(
        CONFIG_COLUMNS,
        dropna=False,
        sort=True,
    )

    total_heatmaps = 0

    for configuration, experiment in configuration_groups:
        settings = dict(zip(CONFIG_COLUMNS, configuration))

        extra_cards = settings["extra_cards"]
        samples = settings["samples"]
        games = settings["games_setting"]
        m = settings["m"]

        output_dir = OUTPUT_ROOT / f"extra_cards_{extra_cards}"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Combine repeated runs with matching configurations.
        grouped = (
            experiment.groupby(["agent_a", "agent_b"], dropna=False)
            .agg(
                total_games=("_games_count", "sum"),
                a_wins_total=("a_wins", "sum"),
                b_wins_total=("b_wins", "sum"),
                a_score_total=("_a_score_total", "sum"),
                b_score_total=("_b_score_total", "sum"),
            )
            .reset_index()
        )

        # Preferred order, matching the agent list in tournament.py
        preferred_order = [
            "RandomPlayer",
            "ZeroOrderPlayer",
            "FirstOrderPlayer",
            "SecondOrderPlayer",
            "ThirdOrderPlayer",
            "FirstOrderMonteCarloPlayer",
            "SecondOrderMonteCarloPlayer",
            "ThirdOrderMonteCarloPlayer",
        ]

        # Include only agents present in this experiment.
        present_agents = set(grouped["agent_a"]) | set(grouped["agent_b"])

        agents = [agent for agent in preferred_order if agent in present_agents]

        # Add any other agents not explicitly listed above.
        agents += sorted(present_agents - set(preferred_order))

        # Initialize matrices. The diagonal remains blank.
        win_matrix = pd.DataFrame(
            np.nan, index=agents, columns=agents
        )
        score_matrix = pd.DataFrame(
            np.nan, index=agents, columns=agents
        )

        for _, matchup in grouped.iterrows():
            a = matchup["agent_a"]
            b = matchup["agent_b"]
            total_games = matchup["total_games"]

            if total_games <= 0:
                continue

            # Win rates are the fraction of games won.
            # Ties are not counted as wins.
            win_matrix.loc[a, b] = (
                matchup["a_wins_total"] / total_games
            )
            win_matrix.loc[b, a] = (
                matchup["b_wins_total"] / total_games
            )

            # Average score per game, weighted across runs.
            score_matrix.loc[a, b] = (
                matchup["a_score_total"] / total_games
            )
            score_matrix.loc[b, a] = (
                matchup["b_score_total"] / total_games
            )

        title_suffix = (
            f"extra_cards={extra_cards}, samples={samples}, "
            f"games={games}, m={m}"
        )

        # Generate the two requested heatmaps.
        plot_heatmap(
            win_matrix,
            f"Win Rate\nextra_cards={extra_cards}, samples={samples}",
            output_dir / f"win_rate_samples_{samples}.png",
            metric="win_rate",
        )

        plot_heatmap(
            score_matrix,
            f"Average Score\nextra_cards={extra_cards}, samples={samples}",
            output_dir / f"average_score_samples_{samples}.png",
            metric="average_score",
        )

        total_heatmaps += 2

        print(f"Generated heatmaps: {output_dir}")

    print(f"\nFinished. Generated {total_heatmaps} heatmaps.")
    print(f"Analysis output: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
