import argparse
import csv
from itertools import product
from pathlib import Path

import openmc
from parametric_model import build_model


# ==========================================
# EXPERIMENT CONFIGURATION
# ==========================================

enrichments = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
moderator_densities = [0.65, 0.70, 0.75, 0.80]

BATCHES = 150
INACTIVE = 50
PARTICLES = 10000

# All 28 combinations.
cases = list(product(enrichments, moderator_densities))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--limit",
    type=int,
    default=None,
    help="Run only the first N cases for testing"
)
args = parser.parse_args()

if args.limit is not None and args.limit < 1:
    parser.error("--limit must be positive")

selected_cases = (
    cases if args.limit is None
    else cases[:args.limit]
)

# ==========================================
# OUTPUT SETUP
# ==========================================

# Keep test runs separate from the completed study.
results_dir = Path(
    "sweep_runs" if args.limit is None else "test_sweep_runs"
)
results_dir.mkdir(exist_ok=True)

csv_path = results_dir / "sweep_summary.csv"

fieldnames = [
    "case_id",
    "enrichment",
    "moderator_density",
    "seed",
    "keff",
    "keff_uncertainty",
    "fuel_flux",
    "fuel_flux_uncertainty",
    "moderator_flux",
    "moderator_flux_uncertainty",
    "fuel_fission",
    "fuel_fission_uncertainty"
]

print(f"Running {len(selected_cases)} simulation cases.")
print(f"Batches: {BATCHES}")
print(f"Inactive batches: {INACTIVE}")
print(f"Particles per batch: {PARTICLES}")

# ==========================================
# RUN PARAMETER SWEEP
# ==========================================

with open(csv_path, "w", newline="") as file:

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for index, (enrichment, density) in enumerate(
        selected_cases, start=1
    ):

        case_id = (
            f"e{enrichment:.1f}_rho{density:.2f}"
            .replace(".", "p")
        )

        seed = 202600 + index

        print(
            f"\n[{index}/{len(selected_cases)}] "
            f"{case_id}",
            flush=True
        )

        # Build the model using our existing function.
        model = build_model(
            enrichment=enrichment,
            moderator_density=density,
            batches=BATCHES,
            inactive=INACTIVE,
            particles=PARTICLES
        )

        model.settings.seed = seed

        # Keep all outputs for this case separate.
        case_dir = results_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        statepoint_path = model.run(
            cwd=case_dir,
            output=False
        )

        # Extract the results.
        with openmc.StatePoint(statepoint_path) as sp:

            keff = sp.keff

            fuel_flux = sp.get_tally(name="fuel_flux")
            moderator_flux = sp.get_tally(
                name="moderator_flux"
            )
            fuel_fission = sp.get_tally(
                name="fuel_fission"
            )

            row = {
                "case_id": case_id,
                "enrichment": enrichment,
                "moderator_density": density,
                "seed": seed,
                "keff": keff.nominal_value,
                "keff_uncertainty": keff.std_dev,
                "fuel_flux": fuel_flux.mean.item(),
                "fuel_flux_uncertainty":
                    fuel_flux.std_dev.item(),
                "moderator_flux":
                    moderator_flux.mean.item(),
                "moderator_flux_uncertainty":
                    moderator_flux.std_dev.item(),
                "fuel_fission":
                    fuel_fission.mean.item(),
                "fuel_fission_uncertainty":
                    fuel_fission.std_dev.item()
            }

            writer.writerow(row)
            file.flush()

            print(
                f"  keff = {keff.nominal_value:.6f} "
                f"+/- {keff.std_dev:.6f}",
                flush=True
            )

print("\n===== SWEEP COMPLETE =====")
print(f"Completed {len(selected_cases)} cases.")
print(f"Results saved to: {csv_path}")
