# ConceptSpectra

ConceptSpectra is a Python package that provides tools for computing the linear and dark energy fluid power spectra in cosmology. It integrates with CLASS (using CLASSY) to compute background quantities, perturbations, and the corresponding power spectrum for various matter species. ConceptSpectra is designed to be flexible. Users may either import the library in their own Python scripts or use the supplied command-line interface.

## Features

- Compute logarithmically spaced k-modes for power spectrum calculations.

- Generate the matter power spectrum for baryons, cold dark matter, and dark energy fluid.

- Use in-memory and on-disk caching to reduce redundant CLASS computations.

- Flexible parameters: Users may supply their own CLASS parameters via the command line.

- Command-line interface for quick simulation runs.

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/your_username/ConceptSpectra.git
```

Change into the repository directory:

```bash
cd ConceptSpectra
```

You may install the package locally using pip (optionally in editable mode):

```bash
pip install -e .
```

Alternatively, you may use the package directly without installation by ensuring that the ConceptSpectra folder is in your Python path.

## Usage

ConceptSpectra can be used in two ways: as an imported module within your own Python scripts or via the command-line interface.

### Library Usage

Below is an example of how to use ConceptSpectra in your own Python script to compute the dark energy fluid power spectrum:

```python
#!/usr/bin/env python3
"""
Example Script: Dark Energy Fluid Power Spectrum using ConceptSpectra

This script demonstrates how to compute the power spectrum for the dark energy fluid ("fld").
"""

import numpy as np
from ConceptSpectra import get_power, get_modes

# Define the cosmological parameters for a model with dark energy fluid.
params = {
    "H0": 67,                  # Hubble constant in km/s/Mpc
    "Omega_b": 0.049,          # Baryon density
    "Omega_cdm": 0.27,         # Cold dark matter density
    "Omega_Lambda": 0,         # No cosmological constant
    "w0_fld": -0.9,            # Equation-of-state parameter for dark energy fluid (w0)
    "wa_fld": 0.1,             # Evolution parameter for dark energy fluid (wa)
    "cs2_fld": 1e-5,           # Sound speed squared for dark energy fluid
    "A_s": 2.1e-9,             # Primordial amplitude
    "n_s": 0.96,               # Spectral index
    "l_max_g": 100,
    "l_max_pol_g": 100,
    "radiation_streaming_approximation": 3,
    "l_max_ur": 100,
    "ur_fluid_approximation": 3,
    "evolver": 0,
    "recfast_Nz0": 1e5,
    "tol_thermo_integration": 1e-6,
    "perturb_sampling_stepsize": 0.01,
    "output": "dTk",
    "gauge": "synchronous",
    "k_output_values": get_modes(1e-3, 3e1, 30, as_str=True)
}

a = 1.0  # Scale factor

# Compute the power spectrum for the dark energy fluid.
modes, de_power = get_power(params, "fld", "nbody", a=a)

# The reduced Hubble parameter h = H0/100 is used for conversion to Mpc/h units.
h = params["H0"] / 100.0

print("Dark Energy Fluid Power Spectrum at scale factor a = {:.3f}".format(a))
print("k-modes (Mpc/h):")
print(modes / h)
print("\nP(k) (scaled by h^3):")
print(de_power * h**3)
```
The above script is available as example.py and can be run as:
```bash
(~/your_concept_path/dep/python/bin/python3 example.py)
```

### Command-Line Interface (CLI) Usage

ConceptSpectra includes a CLI that allows users to specify cosmological parameters. For example, to compute the power spectrum using custom parameters, run:

```bash
python -m ConceptSpectra.cli --H0 70 --Omega_b 0.05 --Omega_cdm 0.25 --w0_fld -1.05 --wa_fld 0.1 --cs2_fld 1e-4 --A_s 2.0e-9 --n_s 0.97 --a 0.8
```

This command will generate an output file (for example, in a directory named Pk) that contains the computed power spectrum data.

## Repository Structure
```bash
ConceptSpectra/
├── __init__.py          # Package initializer; exposes core functions.
├── computations.py      # Contains the core cosmological functions.
└── cli.py               # Command-line interface for executing simulations.
```
## Contributing

Contributions are welcome. If you wish to extend the functionality of ConceptSpectra or report issues, please open an issue or submit a pull request on GitHub.

## License

This project is provided under the MIT License. See the LICENSE file for details.

## Contact

For additional questions, please contact the repository maintainer at tiago.castro@inaf.it.
