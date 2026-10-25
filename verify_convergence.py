from pathlib import Path
import csv

import openmc
import matplotlib.pyplot as plt

from parametric_model import build_model


# Three different random seeds.
seeds = [101, 202, 303]

results_dir = Path("verification_runs")
results_dir.mkdir(exist_ok=True)

results = []

plt.figure(figsize=(10, 5))

for seed in seeds:

    print(f"\nRunning simulation with seed {seed}", flush=True)

    model = build_model(
        enrichment=2.4,
        moderator_density=0.740582,
        batches=150,
        inactive=50,
        particles=10000
    )

    model.settings.seed = seed

    # Track spatial convergence of the fission source.
    entropy_mesh = openmc.RegularMesh()

    # Cover the fuel region in x and y.
    # A single very large axial bin accommodates
    # our infinitely long pin-cell model.
    entropy_mesh.lower_left = (
        -0.39218, -0.39218, -1.0e50
    )
    entropy_mesh.upper_right = (
        0.39218, 0.39218, 1.0e50
    )
    entropy_mesh.dimension = (10, 10, 1)

    model.settings.entropy_mesh = entropy_mesh

    run_dir = results_dir / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    statepoint_path = model.run(
        cwd=run_dir,
        output=False
    )

    with openmc.StatePoint(statepoint_path) as sp:

        keff = sp.keff
        entropy = sp.entropy.copy()

        results.append({
            "seed": seed,
            "keff": keff.nominal_value,
            "uncertainty": keff.std_dev
        })

        print(
            f"keff = {keff.nominal_value:.6f} "
            f"+/- {keff.std_dev:.6f}",
            flush=True
        )

        # Plot Shannon entropy versus batch number.
        batches = range(1, len(entropy) + 1)

        plt.plot(
            batches,
            entropy,
            label=f"Seed {seed}"
        )

# Mark the inactive/active batch boundary.
plt.axvline(
    x=50,
    linestyle="--",
    label="End of inactive batches"
)

plt.xlabel("Batch number")
plt.ylabel("Shannon entropy")
plt.title("Fission Source Convergence")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

figure_path = results_dir / "source_entropy.png"
plt.savefig(figure_path, dpi=200)
plt.close()

# Save independent-run results.
csv_path = results_dir / "independent_seeds.csv"

with open(csv_path, "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["seed", "keff", "uncertainty"]
    )
    writer.writeheader()
    writer.writerows(results)

print("\n===== INDEPENDENT SEED COMPARISON =====")

for result in results:
    print(
        f"Seed {result['seed']}: "
        f"keff = {result['keff']:.6f} "
        f"+/- {result['uncertainty']:.6f}"
    )

print(f"\nSaved CSV: {csv_path}")
print(f"Saved plot: {figure_path}")
print("\nVerification runs completed!")
