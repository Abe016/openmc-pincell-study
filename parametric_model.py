import openmc


def build_model(
    enrichment=2.4,
    moderator_density=0.740582,
    batches=60,
    inactive=15,
    particles=2000
):
    """
    Create a simplified PWR pin-cell model.

    enrichment: U-235 enrichment in uranium, weight %
    moderator_density: Water density in g/cm3
    """

    # Validate input parameters.
    if not 2.0 <= enrichment <= 5.0:
        raise ValueError("Enrichment must be 2.0 to 5.0%.")

    if not 0.65 <= moderator_density <= 0.80:
        raise ValueError("Moderator density must be 0.65 to 0.80 g/cm3.")

    if batches <= inactive or inactive < 0 or particles <= 0:
        raise ValueError("Invalid simulation settings.")

    # ==================================
    # MATERIALS
    # ==================================

    fuel = openmc.Material(name="UO2 Fuel")
    fuel.set_density("g/cm3", 10.29769)

    # One uranium atom per two oxygen atoms.
    # OpenMC calculates isotope fractions.
    fuel.add_element("U", 1.0, enrichment=enrichment)
    fuel.add_nuclide("O16", 2.0)

    clad = openmc.Material(name="Zircaloy")
    clad.set_density("g/cm3", 6.55)

    clad.add_nuclide("Zr90", 2.1827e-2)
    clad.add_nuclide("Zr91", 4.7600e-3)
    clad.add_nuclide("Zr92", 7.2758e-3)
    clad.add_nuclide("Zr94", 7.3734e-3)
    clad.add_nuclide("Zr96", 1.1879e-3)

    water = openmc.Material(name="Borated Water")
    water.set_density("g/cm3", moderator_density)

    water.add_nuclide("H1", 4.9457e-2)
    water.add_nuclide("O16", 2.4672e-2)
    water.add_nuclide("B10", 8.0042e-6)
    water.add_nuclide("B11", 3.2218e-5)

    water.add_s_alpha_beta("c_H_in_H2O")

    # ==================================
    # GEOMETRY
    # ==================================

    fuel_radius = 0.39218
    clad_radius = 0.45720
    pitch = 1.26

    fuel_boundary = openmc.ZCylinder(r=fuel_radius)
    clad_boundary = openmc.ZCylinder(r=clad_radius)

    left = openmc.XPlane(
        x0=-pitch / 2, boundary_type="reflective"
    )
    right = openmc.XPlane(
        x0=pitch / 2, boundary_type="reflective"
    )
    bottom = openmc.YPlane(
        y0=-pitch / 2, boundary_type="reflective"
    )
    top = openmc.YPlane(
        y0=pitch / 2, boundary_type="reflective"
    )

    fuel_cell = openmc.Cell(
        name="Fuel",
        fill=fuel,
        region=-fuel_boundary
    )

    clad_cell = openmc.Cell(
        name="Cladding",
        fill=clad,
        region=+fuel_boundary & -clad_boundary
    )

    water_cell = openmc.Cell(
        name="Water",
        fill=water,
        region=(
            +clad_boundary
            & +left & -right
            & +bottom & -top
        )
    )

    universe = openmc.Universe(
        cells=[fuel_cell, clad_cell, water_cell]
    )

    geometry = openmc.Geometry(universe)

    # ==================================
    # SIMULATION SETTINGS
    # ==================================

    settings = openmc.Settings()
    settings.run_mode = "eigenvalue"
    settings.batches = batches
    settings.inactive = inactive
    settings.particles = particles

    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(
            [-pitch / 2, -pitch / 2, -1],
            [pitch / 2, pitch / 2, 1]
        ),
        constraints={"fissionable": True}
    )

    # ==================================
    # TALLIES
    # ==================================

    # Create reusable cell filters.
    fuel_filter = openmc.CellFilter(fuel_cell)
    moderator_filter = openmc.CellFilter(water_cell)

    # Measure neutron flux in the fuel.
    fuel_flux = openmc.Tally(name="fuel_flux")
    fuel_flux.filters = [fuel_filter]
    fuel_flux.scores = ["flux"]

    # Measure neutron flux in the moderator.
    moderator_flux = openmc.Tally(name="moderator_flux")
    moderator_flux.filters = [moderator_filter]
    moderator_flux.scores = ["flux"]

    # Measure fission reactions in the fuel.
    fuel_fission = openmc.Tally(name="fuel_fission")
    fuel_fission.filters = [fuel_filter]
    fuel_fission.scores = ["fission"]

    # Group the tallies together.
    tallies = openmc.Tallies([
        fuel_flux,
        moderator_flux,
        fuel_fission
    ])

    # ==================================
    # RETURN THE MODEL
    # ==================================

    return openmc.Model(
        materials=[fuel, clad, water],
        geometry=geometry,
        settings=settings,
        tallies=tallies
    )
