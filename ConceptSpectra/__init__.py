"""
ConceptSpectra Package

This package provides functions for computing the cosmological power spectrum of linear
and matter species using the CLASS code. It integrates with CLASSY installed on concept
and offers functionalities for computing background quantities, perturbations, and
generating power spectra.
"""

from .computations import (
    disable_numpy_summarization,
    get_cosmo,
    get_modes,
    get_primordial_curvature_perturbation,
    get_power,
)

__all__ = [
    "disable_numpy_summarization",
    "get_cosmo",
    "get_modes",
    "get_primordial_curvature_perturbation",
    "get_power",
]

