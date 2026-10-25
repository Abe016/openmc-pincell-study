from pathlib import Path
import csv

import openmc
from parametric_model import build_model


# Four controlled test cases.
cases = [
    (2.0, 0.65),
    (2.0, 0.80),
    (5.0, 0.65),
    (5.0, 0.80),
]

results_dir = Path("boron_control_runs")
results_dir.mkdir(exist_ok=True)

results = []

for index, (enrichment, density) in enumerate(cases, 1):

    print(
        f"\nCase {index}: "
        f"Enrichment={enrichment}% "
        f"Density={density} g/cm3",
        flush=True
    )

    # Build our normal model.
    model = build_model(
        enrichment=enrichment,
        moderator_density=density,
        batches=150,
        inactive=50,
        particles=10000
    )

    # Find the water material.
    water = next(
        material for material in model.materials
        if material.name == "Borated Water"
    )

    # Remove boron while keeping the same
    # moderator density and water composition.
    water.remove_nuclide("B10")
    water.remove_nuclide("B11")
    water.name = "Unborated Water"

    # Confirm that boron was removed.
    assert "B10" not in water.get_nuclides()
    assert "B11" not in water.get_nuclides()
    assert abs(water.density - density) < 1e-8

    model.settings.seed = 303000 + index

    case_dir = results_dir / (
        f"e{enrichment:.1f}_rho{density:.2f}"
        .replace(".", "p")
    )
    case_dir.mkdir(parents=True, exist_ok=True)

    statepoint_path = model.run(
        cwd=case_dir,
        output=False
    )

    with openmc.StatePoint(statepoint_path) as sp:

        result = {
            "enrichment": enrichment,
            "moderator_density": density,
            "keff": sp.keff.nominal_value,
            "uncertainty": sp.keff.std_dev
        }

        results.append(result)

        print(
            f"keff = {result['keff']:.6f} "
            f"+/- {result['uncertainty']:.6f}",
            flush=True
        )

# Save results for the final report.
csv_path = results_dir / "unborated_results.csv"

with open(csv_path, "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "enrichment",
            "moderator_density",
            "keff",
            "uncertainty"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

print("\n===== BORON-FREE DENSITY COMPARISON =====")

for enrichment in [2.0, 5.0]:

    low = next(
        r for r in results
        if r["enrichment"] == enrichment
        and r["moderator_density"] == 0.65
    )

    high = next(
        r for r in results
        if r["enrichment"] == enrichment
        and r["moderator_density"] == 0.80
    )

    delta = high["keff"] - low["keff"]

    print(
        f"{enrichment:.1f}% enrichment: "
        f"Density effect = {delta:+.6f}"
    )

print(f"\nResults saved to {csv_path}")
print("Control experiment completed!")
