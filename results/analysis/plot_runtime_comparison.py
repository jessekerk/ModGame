import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "results" / "full_results.csv"
OUTPUT_DIR = Path(__file__).resolve().parent

# Selected matchups: Exact vs Exact and MC vs MC
matchups = {
    # Exact ToM agents
    "Exact ToM1 vs ToM2": (
        "FirstOrderPlayer", "SecondOrderPlayer"
    ),
    "Exact ToM1 vs ToM3": (
        "FirstOrderPlayer", "ThirdOrderPlayer"
    ),
    "Exact ToM2 vs ToM3": (
        "SecondOrderPlayer", "ThirdOrderPlayer"
    ),

    # Monte Carlo ToM agents
    "MC ToM1 vs ToM2": (
        "ToM1 Monte Carlo", "ToM2 Monte Carlo"
    ),
    "MC ToM1 vs ToM3": (
        "ToM1 Monte Carlo", "ToM3 Monte Carlo"
    ),
    "MC ToM2 vs ToM3": (
        "ToM2 Monte Carlo", "ToM3 Monte Carlo"
    ),
}


# --------------------------------------------------
# LOAD RESULTS
# --------------------------------------------------

df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

required_columns = [
    "agent_a",
    "agent_b",
    "extra_cards",
    "runtime_seconds",
    "games",
    "m",
    "samples",
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(
        f"Missing columns in full_results.csv: {missing}. "
        "Make sure tournament.py saves the samples column."
    )

# Ensure numeric columns are interpreted correctly.
for col in ["extra_cards", "runtime_seconds", "games", "m", "samples"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=[
        "extra_cards",
        "runtime_seconds",
        "games",
        "m",
        "samples",
    ]
)


# --------------------------------------------------
# SELECT MATCHUPS
# --------------------------------------------------

results = []

for label, (agent_a, agent_b) in matchups.items():
    selected = df[
        (
            (df["agent_a"] == agent_a)
            & (df["agent_b"] == agent_b)
        )
        | (
            (df["agent_a"] == agent_b)
            & (df["agent_b"] == agent_a)
        )
    ].copy()

    if selected.empty:
        print(f"Warning: no results found for {label}")
        continue

    selected["matchup"] = label
    results.append(selected)

if not results:
    raise ValueError(
        "No matching results found. Check the agent names in full_results.csv."
    )

plot_df = pd.concat(results, ignore_index=True)


# --------------------------------------------------
# GENERATE ONE PLOT PER SAMPLE COUNT
# --------------------------------------------------

summary = (
    plot_df.groupby(["matchup", "extra_cards", "samples"], as_index=False)
    ["runtime_seconds"]
    .mean()
)

for samples, sample_df in summary.groupby("samples"):

    plt.figure(figsize=(10, 6))

    for label, group in sample_df.groupby("matchup"):
        group = group.sort_values("extra_cards")

        plt.plot(
            group["extra_cards"],
            group["runtime_seconds"],
            marker="o",
            linewidth=2,
            label=label,
        )

    plt.xlabel("Number of extra cards")
    plt.ylabel("Runtime per matchup (seconds)")
    plt.title(
        f"Runtime Scaling: Exact ToM vs Monte Carlo\n"
        f"Samples = {int(samples)}"
    )

    plt.xticks(sorted(sample_df["extra_cards"].unique()))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path = OUTPUT_DIR / f"runtime_comparison_samples_{int(samples)}.png"

    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Graph saved to: {output_path.resolve()}")

print("\nFinished generating runtime comparison plots.")


# --------------------------------------------------
# EXTRA PLOTS: RUNTIME VS SAMPLES, PER EXTRA_CARDS
# --------------------------------------------------

for extra_cards in sorted(plot_df["extra_cards"].unique()):

    extra_df = plot_df[plot_df["extra_cards"] == extra_cards].copy()

    # Average repeated measurements for each matchup and sample count.
    runtime_summary = (
        extra_df.groupby(["matchup", "samples"], as_index=False)
        ["runtime_seconds"]
        .mean()
    )

    plt.figure(figsize=(10, 6))

    for label, group in runtime_summary.groupby("matchup"):
        group = group.sort_values("samples")

        plt.plot(
            group["samples"],
            group["runtime_seconds"],
            marker="o",
            linewidth=2,
            label=label,
        )

    plt.xlabel("Number of samples")
    plt.ylabel("Runtime per matchup (seconds)")
    plt.title(f"Runtime vs Samples (Extra Cards = {extra_cards:g})")
    plt.xticks(sorted(runtime_summary["samples"].unique()))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path = (
        OUTPUT_DIR / f"runtime_comparison_extra_{extra_cards:g}.png"
    )

    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Graph saved to: {output_path.resolve()}")

print("\nFinished generating all runtime comparison plots.")