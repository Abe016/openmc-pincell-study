from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Load results from both experiments.
borated = pd.read_csv(
    "sweep_runs/sweep_summary.csv"
)

unborated = pd.read_csv(
    "boron_control_runs/unborated_results.csv"
)

figures_dir = Path("figures")
figures_dir.mkdir(exist_ok=True)

rows = []


# Calculate density effects and uncertainties.
for enrichment in [2.0, 5.0]:
    for label, data in [
        ("With boron", borated),
        ("Without boron", unborated)
    ]:
        subset = data[
            np.isclose(data["enrichment"], enrichment)
        ]

        low = subset[
            np.isclose(subset["moderator_density"], 0.65)
        ].iloc[0]

        high = subset[
            np.isclose(subset["moderator_density"], 0.80)
        ].iloc[0]

        uncertainty_column = (
            "keff_uncertainty"
            if label == "With boron"
            else "uncertainty"
        )

        delta = high["keff"] - low["keff"]

        uncertainty = np.sqrt(
            high[uncertainty_column] ** 2
            + low[uncertainty_column] ** 2
        )

        rows.append({
            "enrichment": enrichment,
            "moderator": label,
            "delta_keff": delta,
            "uncertainty": uncertainty
        })


results = pd.DataFrame(rows)

# Save the comparison for the technical report.
results.to_csv(
    "boron_control_runs/comparison_summary.csv",
    index=False
)

# Create the comparison figure.
fig, ax = plt.subplots(figsize=(9, 6))

for label in ["With boron", "Without boron"]:
    subset = results[
        results["moderator"] == label
    ].sort_values("enrichment")

    ax.errorbar(
        subset["enrichment"],
        subset["delta_keff"],
        yerr=subset["uncertainty"],
        marker="o",
        capsize=5,
        linewidth=2,
        label=label
    )

ax.axhline(0, linestyle="--", color="gray")

ax.set_xticks([2.0, 5.0])
ax.set_xlabel("U-235 Enrichment (weight %)")
ax.set_ylabel("Change in keff")
ax.set_title(
    "Effect of Boron on Moderator Density Sensitivity\n"
    "(0.80 minus 0.65 g/cm³)"
)
ax.legend()
ax.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(
    figures_dir / "boron_control_comparison.png",
    dpi=300
)
plt.close(fig)

print("\n===== BORON CONTROL COMPARISON =====")
print(results.to_string(index=False))
print("\nSaved figure: figures/boron_control_comparison.png")
print("Analysis completed successfully!")
