from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# 1. LOAD AND VERIFY RESULTS
# ==========================================

csv_path = Path("sweep_runs/sweep_summary.csv")
figures_dir = Path("figures")
figures_dir.mkdir(exist_ok=True)

df = pd.read_csv(csv_path)

enrichments = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
densities = [0.65, 0.70, 0.75, 0.80]

# Make sure every expected case exists.
assert len(df) == 28, "Expected 28 simulation results."

assert not df.duplicated(
    subset=["enrichment", "moderator_density"]
).any(), "Duplicate parameter combinations found."

assert not df.isna().any().any(), "Missing data found."

assert set(df["enrichment"]) == set(enrichments)
assert set(df["moderator_density"]) == set(densities)

assert (df["keff_uncertainty"] > 0).all()

print("PASS: All 28 simulation results verified.")


# ==========================================
# 2. KEFF VS ENRICHMENT
# ==========================================

fig, ax = plt.subplots(figsize=(9, 6))

for density in densities:

    subset = df[
        np.isclose(df["moderator_density"], density)
    ].sort_values("enrichment")

    ax.errorbar(
        subset["enrichment"],
        subset["keff"],
        yerr=subset["keff_uncertainty"],
        marker="o",
        capsize=3,
        label=f"{density:.2f} g/cm³"
    )

ax.set_xlabel("U-235 Enrichment (weight %)")
ax.set_ylabel("Effective Multiplication Factor (keff)")
ax.set_title("Effect of Fuel Enrichment on keff")
ax.legend(title="Moderator Density")
ax.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(
    figures_dir / "keff_vs_enrichment.png",
    dpi=300
)
plt.close(fig)


# ==========================================
# 3. MODERATOR DENSITY EFFECT
# ==========================================

low = df[
    np.isclose(df["moderator_density"], 0.65)
].sort_values("enrichment")

high = df[
    np.isclose(df["moderator_density"], 0.80)
].sort_values("enrichment")

# Difference between high and low density.
delta_keff = (
    high["keff"].to_numpy()
    - low["keff"].to_numpy()
)

# Propagate statistical uncertainty for the
# difference between independent simulations.
delta_uncertainty = np.sqrt(
    high["keff_uncertainty"].to_numpy()**2
    + low["keff_uncertainty"].to_numpy()**2
)

fig, ax = plt.subplots(figsize=(9, 6))

ax.errorbar(
    low["enrichment"],
    delta_keff,
    yerr=delta_uncertainty,
    marker="o",
    capsize=4
)

ax.axhline(0, linestyle="--", color="gray")

ax.set_xlabel("U-235 Enrichment (weight %)")
ax.set_ylabel("Change in keff")
ax.set_title(
    "Moderator Density Effect on keff\n"
    "(0.80 minus 0.65 g/cm³)"
)
ax.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(
    figures_dir / "moderator_density_effect.png",
    dpi=300
)
plt.close(fig)


# ==========================================
# 4. FUEL FISSION TALLY
# ==========================================

fig, ax = plt.subplots(figsize=(9, 6))

for density in densities:

    subset = df[
        np.isclose(df["moderator_density"], density)
    ].sort_values("enrichment")

    ax.errorbar(
        subset["enrichment"],
        subset["fuel_fission"],
        yerr=subset["fuel_fission_uncertainty"],
        marker="o",
        capsize=3,
        label=f"{density:.2f} g/cm³"
    )

ax.set_xlabel("U-235 Enrichment (weight %)")
ax.set_ylabel("Fission Reactions per Source Particle")
ax.set_title("Fuel Fission Tally vs Enrichment")
ax.legend(title="Moderator Density")
ax.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(
    figures_dir / "fuel_fission_vs_enrichment.png",
    dpi=300
)
plt.close(fig)


# ==========================================
# 5. PRINT RESULTS SUMMARY
# ==========================================

print("\n===== PARAMETRIC STUDY SUMMARY =====")

print(f"Total cases: {len(df)}")
print(f"Minimum keff: {df['keff'].min():.6f}")
print(f"Maximum keff: {df['keff'].max():.6f}")

print(
    f"Maximum keff uncertainty: "
    f"{df['keff_uncertainty'].max():.6f}"
)

print("\nModerator density effect by enrichment:")

for enrichment, delta, uncertainty in zip(
    low["enrichment"],
    delta_keff,
    delta_uncertainty
):
    print(
        f"  {enrichment:.1f}%: "
        f"{delta:+.6f} +/- {uncertainty:.6f}"
    )

print("\nSaved figures:")
for figure in sorted(figures_dir.glob("*.png")):
    print(f"  {figure}")

print("\nAnalysis completed successfully!")
