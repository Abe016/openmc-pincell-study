## Technical Report

A detailed report covering the simulation methodology,
parameter study, convergence analysis, results, and limitations.

- [Technical Report (PDF)](docs/technical_report.pdf)
- [Technical Report (Markdown)](docs/technical_report.md)

# OpenMC Parametric Neutronics Simulation Study

**Python · OpenMC 0.16.0 · NumPy · Pandas · Matplotlib**

A reproducible Monte Carlo neutron-transport study of a **simplified, reflective pressurized water reactor (PWR) fuel pin cell**. The project uses the OpenMC Python API to automate a two-parameter study of U-235 enrichment and moderator density, quantify statistical uncertainty, and investigate the role of boron absorption through additional control simulations.

> **Scope:** Educational reactor-physics sensitivity study, **not** a full reactor-core model, operating digital twin, validated reactor design, or safety analysis. The pin-cell geometry and initial compositions were adapted from OpenMC's PWR pin-cell example; the parameterization, automation, verification, and analysis form the project work.

## Main results

- **28 primary cases:** 7 enrichment levels (2.0%–5.0% U-235 by uranium weight) × 4 moderator densities (0.65–0.80 g/cm³).
- **4 control cases:** With boron removed at 2.0% and 5.0% enrichment, at the two endpoint moderator densities.
- **Calculated $k_{\mathrm{eff}}$ range in the main sweep:** 1.096075–1.353420.
- **Largest reported $k_{\mathrm{eff}}$ standard uncertainty in the main sweep:** 0.001151.
- **Per main case:** 150 batches, 50 inactive batches, 10,000 particles per batch (1,000,000 active particle histories).
- **Additional outputs:** source-normalized fuel flux, moderator flux, and fuel fission-reaction tallies, each with statistical uncertainty.

Across all four tested moderator densities, higher U-235 enrichment increased the calculated neutron multiplication factor. The impact of moderator density depended on enrichment and whether boron was present.

### Moderator-density comparison

Change defined as $\Delta k_{\mathrm{eff}} = k_{\mathrm{eff}}(0.80\,\mathrm{g/cm^3}) - k_{\mathrm{eff}}(0.65\,\mathrm{g/cm^3})$.

| Enrichment | Borated water | Unborated-water control |
|---|---:|---:|
| 2.0% | −0.009515 ± 0.001236 | +0.020118 ± 0.001255 |
| 5.0% | +0.010456 ± 0.001364 | +0.036469 ± 0.001284 |

Uncertainties shown are propagated one-standard-deviation Monte Carlo statistical uncertainties. In the borated cases, increasing the moderator material density also increases boron atom density because material composition is held fixed. Removing boron at fixed **total moderator mass density** changes the remaining H/O atom densities slightly. Thus, these comparisons **support an important role for boron absorption**, but do not uniquely isolate every physical mechanism.

## Scientific figures

| Figure | Description |
|---|---|
| `figures/keff_vs_enrichment.png` | $k_{\mathrm{eff}}$ against enrichment at four moderator densities, with statistical error bars |
| `figures/moderator_density_effect.png` | Endpoint density effect (0.80 minus 0.65 g/cm³) against enrichment |
| `figures/fuel_fission_vs_enrichment.png` | Source-normalized fuel fission tally against enrichment |
| `figures/boron_control_comparison.png` | Endpoint density response in borated and unborated models |
| `figures/source_entropy.png` | Spatial fission-source Shannon entropy by batch for three random seeds |

![Neutron multiplication across the enrichment sweep](figures/keff_vs_enrichment.png)

![Effect of moderator density across enrichment](figures/moderator_density_effect.png)

![Boron control comparison](figures/boron_control_comparison.png)

## Model and assumptions

The model represents an axially infinite fuel pin with:

- UO₂ fuel (density **10.29769 g/cm³**) with configurable U-235 enrichment;
- Zircaloy cladding (density **6.55 g/cm³**);
- borated-water moderator with configurable density;
- concentric cylindrical fuel/cladding boundaries and square reflective lateral boundaries;
- OpenMC continuous-energy neutron transport in k-eigenvalue mode.

Reference dimensions: fuel radius **0.39218 cm**, outer cladding radius **0.45720 cm**, and square pitch **1.26 cm**. Reflective boundaries approximate an infinite repeating pin lattice and eliminate lateral neutron leakage; these conditions do **not** represent a finite reactor core. The model is adapted from OpenMC's example, with a programmatic uranium enrichment specification.

The calculations used **OpenMC 0.16.0** and the **ENDF/B-VIII.1 HDF5 nuclear data** installed locally. The execution output reported cross-section/thermal-scattering data at **294 K**; changing moderator density here is a controlled numerical sensitivity exercise, **not** a coupled temperature–density or realistic hot-reactor transient calculation. The model does not incorporate thermal-hydraulic feedback, fuel depletion, realistic core leakage, or real operating measurements.

## Verification and numerical checks

- **Input verification:** Python assertions checked 2.4% and 3.5% uranium enrichments and a change in moderator density to 0.65 g/cm³.
- **Reference reproduction:** A manually constructed baseline model reproduced the reference-example result with matching inputs and random number sequence. This is implementation verification, not independent physical validation.
- **Statistical precision:** Three active-history configurations (90,000; 400,000; 1,000,000) reduced the reported $k_{\mathrm{eff}}$ standard uncertainty from approximately 0.003204 to 0.000977.
- **Independent seed checks:** Seeds 101, 202, and 303 returned $k_{\mathrm{eff}}$ estimates of 1.161331 ± 0.000897, 1.159469 ± 0.000937, and 1.160110 ± 0.000812.
- **Fission-source convergence:** Shannon entropy remained approximately stable before and after the 50-inactive-batch boundary in the checked baseline configurations.
- **Data completeness:** The analysis script checks for exactly 28 unique enrichment–density combinations, missing values, and positive reported uncertainty.

These checks support the **baseline numerical workflow** but do not replace comparison with a trusted external benchmark or verification of every parameter point's fission-source convergence.

## Repository organization

```text
.
├── parametric_model.py                 # materials, geometry, settings, tallies
├── run_sweep.py                       # main 28-case simulation campaign
├── analyze_sweep.py                   # numerical summary and primary figures
├── check_boron_effect.py              # four unborated-water control cases
├── analyze_boron_control.py           # control comparison and figure
├── run_convergence.py                 # particle-history precision comparison
├── verify_convergence.py              # random seeds and source entropy
├── verify_parameters.py               # checks input material parameters
├── environment.yml                    # conda environment specification
├── sweep_runs/sweep_summary.csv
├── boron_control_runs/
│   ├── unborated_results.csv
│   └── comparison_summary.csv
├── convergence_runs/convergence_summary.csv
├── verification_runs/independent_seeds.csv
└── figures/                            # five scientific figures
```

OpenMC-generated `statepoint.*.h5`, `summary.h5`, and model XML files are **not committed**; the simulation scripts can regenerate them when the nuclear data and OpenMC installation are available. The processed CSV files and figures are included for inspection without requiring an immediate simulation rerun.

## Getting started

### 1. Install software

The original development environment used **WSL 2 / Ubuntu**, **Miniforge/Conda**, and OpenMC 0.16.0. A Linux installation is recommended for following these instructions.

```bash
conda env create -f environment.yml
conda activate openmc-pincell
```

### 2. Install and configure nuclear data

Obtain an appropriate **ENDF/B-VIII.1 HDF5** continuous-energy library from the [OpenMC nuclear data downloads](https://openmc.org/data/). Set the environment variable to the **existing** `cross_sections.xml` file for that library:

```bash
export OPENMC_CROSS_SECTIONS="/absolute/path/to/cross_sections.xml"
test -f "$OPENMC_CROSS_SECTIONS" && echo "Nuclear data configured"
```

The nuclear data are **not** bundled in this repository. The correct data library and temperature coverage matter when comparing or interpreting results.

### 3. Reproduce the saved-data analysis (no neutron transport required)

From the repository root, run:

```bash
python verify_parameters.py
python analyze_sweep.py
python analyze_boron_control.py
```

These steps check material-input construction and regenerate the main figures using the committed CSV datasets.

### 4. Run Monte Carlo simulations (optional)

**Important:** Running the full sweep **replaces** the existing `sweep_runs/sweep_summary.csv` and regenerates case output files. Preserve a copy of the archived results or run in a fresh clone if you want to compare datasets.

```bash
python run_sweep.py
python check_boron_effect.py
python run_convergence.py
python verify_convergence.py
```

For a short sweep smoke test, use `python run_sweep.py --limit 2` **only after** updating `run_sweep.py` so test runs write to `test_sweep_runs/` rather than overwriting `sweep_runs/sweep_summary.csv`.

Monte Carlo estimates may differ slightly if seeds, hardware, software versions, model inputs, or nuclear-data versions change. Results from all cases include stochastic uncertainty.

## Limitations and interpretation

1. **Simplified geometry:** A reflective pin-cell is not a full fuel assembly or finite power reactor; core-level conclusions cannot be drawn directly.
2. **Thermal assumptions:** The nuclear data used in these runs were reported at 294 K, while moderator density was independently varied. This is not a realistic coupled thermal feedback model.
3. **Composition effects:** In the borated sweep, water and boron number densities change together at fixed relative isotope composition. Removing boron at fixed mass density changes the H/O atom densities as well.
4. **Source normalization:** OpenMC's flux and fission tallies are normalized per source particle, **not** absolute neutron flux in particles/cm²/s or fissions/s. A total power or source-rate normalization and appropriate geometric volume treatment would be needed for those units.
5. **Statistical vs. modeling uncertainty:** Reported ± uncertainties are Monte Carlo sampling errors, not bounds on cross-section, geometry, modeling, or physical assumptions.
6. **Nuclear-data warning:** Some runs reported a negative probability-table entry for Zr-96 at 294 K. Runs completed, but its possible numerical/data-processing significance was **not quantified**. The study should not be presented as benchmark-validated or safety-grade.
7. **Unverified broader parameter space:** Numerical source-convergence checks were performed for the baseline conditions, not for each of the 28 sweep cases.

## Project takeaway

This project demonstrates the ability to construct and parameterize a nuclear simulation model; automate scientific simulations using Python; save structured outputs; evaluate Monte Carlo uncertainty and fission-source behavior; use a controlled follow-up experiment to investigate an observed trend; and communicate results with appropriate limitations.

## References

- [OpenMC documentation](https://docs.openmc.org/en/stable/)
- [OpenMC installation and configuration](https://docs.openmc.org/en/stable/usersguide/install.html)
- [OpenMC tallies and tally normalization](https://docs.openmc.org/en/stable/usersguide/tallies.html)
- [OpenMC data libraries](https://openmc.org/data/)
- [OpenMC project and source code](https://github.com/openmc-dev/openmc)
