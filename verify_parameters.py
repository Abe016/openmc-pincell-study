from parametric_model import build_model


def verify_case(enrichment, moderator_density):
    model = build_model(
        enrichment=enrichment,
        moderator_density=moderator_density
    )

    # Find the fuel and water materials.
    fuel = next(
        m for m in model.materials
        if m.name == "UO2 Fuel"
    )

    water = next(
        m for m in model.materials
        if m.name == "Borated Water"
    )

    # Calculate the U-235 mass fraction among uranium isotopes.
    uranium_isotopes = fuel.get_nuclides("U")

    total_uranium_mass_density = sum(
        fuel.get_mass_density(nuclide)
        for nuclide in uranium_isotopes
    )

    u235_mass_density = fuel.get_mass_density("U235")

    calculated_enrichment = (
        100 * u235_mass_density / total_uranium_mass_density
    )

    print(f"\nRequested enrichment: {enrichment:.2f}%")
    print(f"Calculated enrichment: {calculated_enrichment:.2f}%")
    print(f"Uranium isotopes: {uranium_isotopes}")
    print(f"Fuel density: {fuel.density:.6f} g/cm3")
    print(f"Moderator density: {water.density:.6f} g/cm3")

    # Verify the model matches the requested inputs.
    assert abs(calculated_enrichment - enrichment) < 0.02
    assert abs(water.density - moderator_density) < 1e-8

    print("PASS: Material parameters verified.")


verify_case(2.4, 0.740582)
verify_case(3.5, 0.740582)
verify_case(2.4, 0.650000)

print("\nAll material verification tests passed!")
