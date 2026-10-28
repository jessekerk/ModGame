# ModGame: Theory of Mind Agents

This project evaluates Theory of Mind (ToM) agents in ModGame, comparing their win rates and average scores against other agents. It also compares exact ToM implementations with Monte Carlo optimized versions.

## Project Structure

```text
ModGame/
├── agents/
│   ├── monte_carlo_sampling_utils.py
│   ├── random_player.py
│   ├── zero_order_player.py
│   ├── first_order_player.py
│   ├── second_order_player.py
│   ├── third_order_player.py
│   ├── ToM1_MonteCarlo.py
│   ├── ToM2_MonteCarlo.py
│   ├── ToM3_MonteCarlo.py
│   ├── ToM1_MonteCarlo_Optimized.py
│   ├── ToM2_MonteCarlo_Optimized.py
│   ├── ToM3_MonteCarlo_Optimized.py
├── main.py
├── tournament.py
├── modgame.py
├── requirements.txt
├── results/
│   ├── full_results.csv
│   └── analysis/
│       ├── analyze_results.py
│       ├── plot_runtime_comparison.py
│       └── extra_cards_*/
├── old_monte_carlo_results/
│   ├── extra_cards_0/
│   ├── extra_cards_1/
│   ├── extra_cards_2/
│   ├── extra_cards_3/
│   └── extra_cards_4/
└── README.md
```

- `main.py`: Runs the experiments.
- `tournament.py`: Runs pairwise agent matchups and records wins, scores, and runtime.
- `results/full_results.csv`: Previously generated experiment results, included to avoid rerunning the full experiment suite.
- `results/analysis/`: Scripts and outputs for analysing results and generating heatmaps and runtime comparisons.
- `old_monte_carlo_results/`: Heatmaps from earlier Monte Carlo experiments before optimizing.

## Setup

Use Python 3 and install the required dependencies:

```bash
pip install -r requirements.txt
```

Run all commands from the project root directory.

## Running Experiments

To run the experiments:

```bash
python main.py
```

You can choose your own configuration for what experiments you want to run.

**Warning:** Running the full experiment suite can take several hours. Existing results are available in `results/full_results.csv`, so rerunning the experiments is not necessary to reproduce the existing analysis.

## Generating Heatmaps

To generate heatmaps from the available results:

```bash
python results/analysis/analyze_results.py
```

The generated heatmaps are saved under `results/analysis/`, organised by configuration.

**Current coverage:** The heatmaps generated from the current (updated Monte Carlo) results are complete only for `extra_cards = 0` and `extra_cards = 3`, with `samples = 25`. Other configurations may have incomplete results. Generating complete heatmaps for all configurations requires running the missing experiments, which may take a few hours in total.

The `old_monte_carlo_results/` directory contains heatmaps from earlier Monte Carlo experiments for `extra_cards = 0` through `4`.


## Generating Runtime Comparison

To generate the runtime comparison from the available results:

```bash
python results/analysis/plot_runtime_comparison.py
```

**Current coverage:** The comparisons generated from the results are plotting either the extra cards or the samples on the horizontal axes. They are complete for `samples = 25` and `samples = 100`, with `samples = 25`. Although, the other plots still have interesting datapoints in the plots. Generating complete heatmaps for all configurations requires running the missing experiments, which may take a few hours in total.

## Reproducing Results

1. Clone the repository.
2. Install the dependencies.
3. Use the committed `results/full_results.csv` to reproduce the available analysis and heatmaps.
4. To reproduce the complete experiment suite from scratch, run `python main.py`. This may take several hours.
