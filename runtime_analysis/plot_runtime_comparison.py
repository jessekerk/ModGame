import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load tournament results
csv_path = Path("runtime_analysis") / "runtime_results.csv"
df = pd.read_csv(csv_path)

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

# Select rows, regardless of matchup order
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
    raise ValueError("No matching results found. Check the CSV path and agent names.")

plot_df = pd.concat(results, ignore_index=True)

# Average repeated measurements, if present
summary = (
    plot_df.groupby(["matchup", "extra_cards"], as_index=False)
    ["runtime_seconds"]
    .mean()
)

# Plot
plt.figure(figsize=(10, 6))

for label, group in summary.groupby("matchup"):
    group = group.sort_values("extra_cards")
    plt.plot(
        group["extra_cards"],
        group["runtime_seconds"],
        marker="o",
        linewidth=2,
        label=label,
    )

plt.xlabel("Number of extra cards")
plt.ylabel("Runtime for 1,000 games (seconds)")
plt.title("Runtime scaling: Exact ToM vs Monte Carlo")
plt.xticks(sorted(summary["extra_cards"].unique()))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

output_path = Path("runtime_analysis/runtime_comparison.png")
plt.savefig(output_path, dpi=200)
print(f"Graph saved to: {output_path.resolve()}")

plt.show()
