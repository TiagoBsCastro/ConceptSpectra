"""
Command-Line Interface (CLI) for ConceptSpectra

This module provides a command-line interface for computing spectra.
Users can supply their own cosmological parameters as command-line arguments to generate
the linear matter power spectrum.
"""
import argparse
import os
import sys
import numpy as np

from .computations import get_modes, get_power

def run_simulation(user_params):
    """
    Run the spectra computation with user-specified parameters.

    Merges user-specified parameters with default cosmological settings,
    computes the power spectrum for the specified species at a given scale factor,
    and writes the results to a text file.

    Parameters:
        user_params (dict): Dictionary of user-specified parameters that override the defaults.

    Returns:
        None.
    """
    # Default parameters for the simulation
    defaults = {
        # Cosmology parameters
        "H0": 67,
        "Omega_b": 0.049,
        "Omega_cdm": 0.27,
        "Omega_Lambda": 0,
        "w0_fld": -1,
        "wa_fld": 0,
        "cs2_fld": 1e-5,
        # Primordial spectrum parameters
        "A_s": 2.1e-9,
        "n_s": 0.96,
        # Photon precision parameters
        "l_max_g": 100,
        "l_max_pol_g": 100,
        "radiation_streaming_approximation": 3,
        # Massless neutrino precision parameters
        "l_max_ur": 100,
        "ur_fluid_approximation": 3,
        # General precision parameters
        "evolver": 0,
        "recfast_Nz0": 1e5,
        "tol_thermo_integration": 1e-6,
        "perturb_sampling_stepsize": 0.01,
        # Output settings and gauge
        "output": "dTk",
        "gauge": "synchronous",
        "P_k_max_1/Mpc": 0,
    }
    # Update defaults with user parameters
    defaults.update(user_params)

    k_min = 1e-3  # Mpc⁻¹
    k_max = 1e1   # Mpc⁻¹
    modes_per_decade = 30
    defaults["k_output_values"] = get_modes(k_min, k_max, modes_per_decade, as_str=True)

    # Determine the scale factor at which to compute the spectrum (default is 1)
    a = defaults.get("a", 1.0)
    defaults.pop('a', None)

    # Get the species to be computed (default is "b + cdm")
    species = defaults.get("species", "b + cdm")
    defaults.pop("species", None)

    # Compute the power spectrum for the chosen species
    modes, power = get_power(defaults, species, "nbody", a=a)

    h = defaults["H0"] / 100
    output_file = f"Pk/powerspec-{species}-a={a:4.3f}"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    np.savetxt(output_file, np.transpose([modes / h, power * h**3]))
    print(f"Saved power spectrum for species '{species}' to {output_file}")


def main():
    """
    Entry point for the command-line interface.

    Parses command-line arguments to obtain cosmological parameters and the species parameter,
    and calls run_simulation.

    Returns:
        None.
    """
    parser = argparse.ArgumentParser(
        description="Run CLASS cosmology simulation with user-specified parameters using ConceptSpectra."
    )
    # Cosmology parameters
    parser.add_argument("--H0", type=float, default=67, help="Hubble constant [default: 67]")
    parser.add_argument("--Omega_b", type=float, default=0.049, help="Baryon density [default: 0.049]")
    parser.add_argument("--Omega_cdm", type=float, default=0.27, help="Cold dark matter density [default: 0.27]")
    parser.add_argument("--Omega_Lambda", type=float, default=0, help="Dark energy density [default: 0]")
    parser.add_argument("--w0_fld", type=float, default=-1, help="w0 for dark energy fluid [default: -1]")
    parser.add_argument("--wa_fld", type=float, default=0, help="wa for dark energy fluid [default: 0]")
    parser.add_argument("--cs2_fld", type=float, default=1e-5, help="Sound speed squared for dark energy fluid [default: 1e-5]")
    # Primordial spectrum parameters
    parser.add_argument("--A_s", type=float, default=2.1e-9, help="Primordial amplitude [default: 2.1e-9]")
    parser.add_argument("--n_s", type=float, default=0.96, help="Primordial spectral index [default: 0.96]")
    # Other parameters
    parser.add_argument("--a", type=float, default=1.0, help="Scale factor [default: 1.0]")
    parser.add_argument("--species", type=str, default="b + cdm", 
                        help="Species for which to compute the power spectrum (e.g., 'b + cdm', 'fld', etc.) [default: 'b + cdm']")
    args = parser.parse_args()

    # Convert parsed arguments to a dictionary
    user_params = vars(args)
    run_simulation(user_params)


if __name__ == "__main__":
    main()

