from pathlib import Path
import csv

import openmc
from parametric_model import build_model


# Different simulation configurations to compare.
configurations = [
    ("initial", 60, 15, 2000),
    ("medium", 120, 40, 5000),
    ("high", 150, 50, 10000),
]

results_dir = Path("convergence_runs")
results_dir.mkdir(exist_ok=True)

results = []

for name, batches, inactive, particles in configurations:

    print(f"\nRunning configuration: {name}", flush=True)
    print(f"  Batches: {batches}", flush=True)
    print(f"  Inactive: {inactive}", flush=True)
    print(f"  Particles/batch: {particles}", flush=True)

    model = build_model(
        enrichment=2.4,
        moderator_density=0.740582,
        batches=batches,
        inactive=inactive,
        particles=particles
    )

    # Use a consistent random seed for reproducibility.
    model.settings.seed = 12345

    run_dir = results_dir / name
    run_dir.mkdir(parents=True, exist_ok=True)

    # Run without displaying every OpenMC batch.
    statepoint_path = model.run(
        cwd=run_dir,
        output=False
    )

    with openmc.StatePoint(statepoint_path) as sp:

        keff = sp.keff

        fuel_flux = sp.get_tally(name="fuel_flux")
        moderator_flux = sp.get_tally(name="moderator_flux")
        fuel_fission = sp.get_tally(name="fuel_fission")

        result = {
            "name": name,
            "batches": batches,
            "inactive": inactive,
            "particles": particles,
            "active_histories": (batches - inactive) * particles,
            "keff": keff.nominal_value,
            "keff_uncertainty": keff.std_dev,
            "fuel_flux": fuel_flux.mean.item(),
            "fuel_flux_uncertainty": fuel_flux.std_dev.item(),
            "moderator_flux": moderator_flux.mean.item(),
            "moderator_flux_uncertainty": moderator_flux.std_dev.item(),
            "fuel_fission": fuel_fission.mean.item(),
            "fuel_fission_uncertainty": fuel_fission.std_dev.item()
        }

        results.append(result)

        print(
            f"  keff = {result['keff']:.6f} "
            f"+/- {result['keff_uncertainty']:.6f}",
            flush=True
        )

        print(
            f"  Fuel fission = {result['fuel_fission']:.6f} "
            f"+/- {result['fuel_fission_uncertainty']:.6f}",
            flush=True
        )

# Save all results.
csv_path = results_dir / "convergence_summary.csv"

with open(csv_path, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("\n===== CONVERGENCE COMPARISON =====")

for result in results:
    print(
        f"{result['name']:8s} | "
        f"Histories: {result['active_histories']:>8,d} | "
        f"keff: {result['keff']:.6f} "
        f"+/- {result['keff_uncertainty']:.6f}"
    )

print(f"\nResults saved to: {csv_path}")
print("Convergence study completed!")
