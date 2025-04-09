"""
Example Script: Dark Energy Fluid Power Spectrum

This script demonstrates how to compute the power spectrum for the dark energy fluid ("fld")
using the ConceptSpectra package. The DE fluid power spectrum is more unusual and can be of great
interest. The script sets up a custom cosmology, computes the DE fluid power spectrum, and prints
the results.

Usage:
    python example_de_pk.py
"""

import numpy as np
from ConceptSpectra import get_power, get_modes

# Define the cosmological parameters for a model with a dark energy fluid.
params = {
    # Cosmology parameters (with no cosmological constant; DE fluid is used instead)
    "H0": 67,                  # Hubble constant in km/s/Mpc
    "Omega_b": 0.049,          # Baryon density parameter
    "Omega_cdm": 0.27,         # Cold dark matter density parameter
    "Omega_Lambda": 0,         # No cosmological constant since DE fluid is used
    "w0_fld": -0.9,            # Dark energy fluid equation-of-state parameter, w0
    "wa_fld": 0.1,             # Dark energy fluid evolution parameter, wa
    "cs2_fld": 1e-5,           # Sound speed squared for the dark energy fluid
    "use_ppf": "no",           # Use ppf or fluid DE description
    # Primordial spectrum parameters
    "A_s": 2.1e-9,             # Amplitude of primordial perturbations
    "n_s": 0.96,               # Spectral index
    # Precision parameters for CLASS
    "l_max_g": 100,
    "l_max_pol_g": 100,
    "radiation_streaming_approximation": 3,
    "l_max_ur": 100,
    "ur_fluid_approximation": 3,
    "evolver": 0,
    "recfast_Nz0": 1e5,
    "tol_thermo_integration": 1e-6,
    "perturb_sampling_stepsize": 0.01,
    # Output settings
    "output": "dTk",
    # Generate modes as a formatted string using ConceptSpectra's get_modes
    "k_output_values": get_modes(1e-3, 1e1, 30, as_str=True)
}

# Set the scale factor at which to compute the power spectrum.
# Here we choose a = 1.0, but this can be modified as needed.
a = 1.0

# Compute the DE fluid power spectrum using the "fld" species.
# Using the "nbody" gauge transformation for an example.
modes, de_power = get_power(params, "fld", "nbody", a=a)

# Rescale the k-modes and power spectrum for conventional usage.
# The reduced Hubble parameter h = H0/100 is used to obtain units of Mpc/h.
h = params["H0"] / 100.0

# Plot the computed results.
import matplotlib.pyplot as plt
plt.loglog(modes / h, de_power * h**3)
plt.xlabel(r"$k\,[{\rm Mpc}^{-1}\,h]$")
plt.ylabel(r"$P(k)\,[{\rm Mpc}^{3}\,h^{-3}]$")
plt.title("Dark Energy Fluid (DE fluid) Power Spectrum at scale factor a = {:.3f}".format(a))
plt.savefig("Pk-DE.pdf")
