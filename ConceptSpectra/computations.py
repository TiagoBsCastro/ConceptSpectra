"""
Computations Module for ConceptSpectra

This module provides functions to perform cosmological computations using the CLASS code.
It includes functions for managing caching of computed results, computing background and 
perturbation data, and generating power spectra for linear and matter species.
"""

import contextlib
import functools
import hashlib
import os
import pathlib
import pickle
import sys

import numpy as np
import scipy.interpolate
import classy


@contextlib.contextmanager
def disable_numpy_summarization():
    """
    Context manager to disable numpy array summarization.

    Temporarily sets the numpy print option "threshold" to infinity so that entire arrays
    are printed. The original threshold is restored when exiting the context.

    Yields:
        None.
    """
    threshold = np.get_printoptions()["threshold"]
    np.set_printoptions(threshold=np.inf)
    try:
        yield
    finally:
        np.set_printoptions(threshold=threshold)


def get_cosmo(params=None, cache_mem=None, cache_disk=None):
    """
    Compute cosmological background and perturbations using CLASS.

    This function computes and returns the cosmological background and perturbations based on 
    the provided CLASS parameters. Caching is used both in memory and on disk to avoid redundant 
    computations.

    Parameters:
        params (dict, optional): Dictionary of CLASS parameters. Defaults to {}.
        cache_mem (dict, optional): In-memory cache for computed values. Defaults to an empty dict.
        cache_disk (pathlib.Path, optional): Path for disk cache. Defaults to a ".class-cache" directory
            in the current file's folder.

    Returns:
        tuple: A tuple (modes, bg, pts) where:
               - modes (np.ndarray): Array of computed modes.
               - bg (dict): Background quantities.
               - pts (dict): Perturbation data.

    Raises:
        RuntimeError: If required parameters are not provided or CLASS computation fails.
    """
    if cache_mem is None:
        cache_mem = {}
    if cache_disk is None:
        cache_disk = pathlib.Path(__file__).absolute().parent / ".class-cache"
    if params is None:
        params = {}
    # Generate cache key from sorted parameters
    params = {key: params[key] for key in sorted(params)}
    cache_key = hashlib.sha512(
        ((str(params)[1:-1] + ",").replace(".0,", ",") + classy.__file__).encode("utf-8")
    ).hexdigest()[:16]
    cache_disk /= f"{cache_key}.pickle"
    # Look up in caches
    if (loot := cache_mem.get(cache_key)) is not None:
        return loot
    if os.environ.get("classcache") != "0" and cache_disk.exists():
        with open(cache_disk, "rb") as f:
            try:
                params_disk, modes, bg, pts = pickle.load(f)
            except Exception:
                print(f"Warning: Failed to load {cache_disk}", file=sys.stderr)
            else:
                if params_disk == params:
                    return modes, bg, pts
                print(f"Warning: Parameter mismatch in {cache_disk}", file=sys.stderr)
    # Run CLASS
    cosmo = classy.Class()
    cosmo.set(params)
    print("Calling CLASS", end=" ...", flush=True)
    cosmo.compute()
    print(" done")
    bg = cosmo.get_background()
    pts = cosmo.get_perturbations().get("scalar", {})
    modes = None
    if pts:
        if "k_output_values" not in params:
            raise RuntimeError(
                "Please specify k_output_values in CLASS params when running with perturbations"
            )
        modes = np.fromstring(params["k_output_values"], sep=",")
    # Store in caches
    cache_mem[cache_key] = (modes, bg, pts)
    if os.environ.get("classcache") != "0":
        os.makedirs(cache_disk.parent, exist_ok=True)
        with open(cache_disk, "wb") as f:
            pickle.dump((params, modes, bg, pts), f)
    return modes, bg, pts


def get_modes(k_min, k_max, modes_per_decade, as_str=False, n_decimals=3):
    """
    Generate an array of modes between k_min and k_max.

    Returns a logarithmically spaced array of modes. Optionally, the modes may be returned
    as a formatted string.

    Parameters:
        k_min (float): Minimum value of k.
        k_max (float): Maximum value of k.
        modes_per_decade (float): Number of modes per decade.
        as_str (bool, optional): If True, returns the modes as a formatted string. Defaults to False.
        n_decimals (int, optional): Number of decimals for formatting. Defaults to 3.

    Returns:
        np.ndarray or str: Array of modes or a formatted string of modes.
    """
    n_modes = int(round(modes_per_decade * np.log10(k_max / k_min)))
    modes = np.logspace(np.log10(k_min), np.log10(k_max), n_modes)
    if not as_str:
        return modes
    with disable_numpy_summarization():
        return np.array2string(
            modes,
            max_line_width=np.inf,
            formatter={
                "float": functools.partial(
                    lambda k: f"{{:.{n_decimals - 1}e}}".format(k)
                )
            },
            separator=",",
        ).strip("[]")


def get_primordial_curvature_perturbation(params, modes):
    """
    Compute the primordial curvature perturbation.

    This function calculates the primordial curvature perturbation for the provided modes
    using the CLASS parameters.

    Parameters:
        params (dict): Dictionary of CLASS parameters. Must include "A_s" and "n_s".
        modes (np.ndarray): Array of k modes.

    Returns:
        np.ndarray: Array of computed primordial curvature perturbations.

    Raises:
        RuntimeError: If required parameters ("A_s" or "n_s") are missing.
    """
    for param in ["A_s", "n_s"]:
        if param not in params:
            raise RuntimeError(f'Please specify "{param}" in the CLASS parameters')
    A_s = params["A_s"]
    n_s = params["n_s"]
    alpha_s = params.get("alpha_s", 0)
    pivot = params.get("k_pivot", 0.05)  # Mpc⁻¹
    return (
        np.pi
        * np.sqrt(2 * A_s)
        * modes ** (-3 / 2)
        * (modes / pivot) ** ((n_s - 1) / 2)
        * np.exp(alpha_s / 4 * np.log(modes / pivot) ** 2)
    )


def get_power(params, species, gauge="synchronous", *, a=None, z=None):
    """
    Compute the power spectrum for specified species.

    Calculates the power spectrum by interpolating background and perturbation
    quantities at a given scale factor. The result is computed for a combination of species.

    Parameters:
        params (dict): CLASS parameters dictionary.
        species (str): Species or combination of species (use '+' to combine, e.g., "b + cdm").
        gauge (str, optional): Gauge to be used; allowed values are "synchronous" or "nbody". Defaults to "synchronous".
        a (float, optional): Scale factor. If not provided, may be computed from z.
        z (float, optional): Redshift. Either a or z should be provided, but not both.

    Returns:
        tuple: (modes, power_spectrum), where 'modes' is a numpy array of k values and 'power_spectrum'
               is a numpy array of the computed power spectrum.

    Raises:
        RuntimeError: If input parameters are inconsistent or required data is missing.
    """
    if gauge.lower().startswith("sync"):
        gauge = "synchronous"
    elif "body" in gauge.lower():
        gauge = "nbody"
    else:
        raise RuntimeError(f'Unknown gauge "{gauge}"')
    if not params.get("gauge", "synchronous").lower().startswith("sync"):
        raise RuntimeError(
            'Please do not set the CLASS "gauge" parameter to anything but "synchronous"'
        )
    params["P_k_max_1/Mpc"] = 0
    if a is None and z is None:
        a = 1
    elif a is None:
        a = 1 / (1 + z)
    elif a is not None and z is None:
        pass
    else:
        raise RuntimeError("Do not supply both a and z")
    loga = np.log(a)
    modes, bg, pts = get_cosmo(params)
    if not pts:
        raise RuntimeError("Cannot compute power as no perturbations are present")
    if modes.size != len(pts):
        raise RuntimeError(f"modes.size == {modes.size} != len(pts) == {len(pts)}")

    def split_species(s):
        return s.replace(" ", "").split("+")
    species_unique = sorted(set(split_species(species)))
    # Interpolate background quantities in time
    loga_bg = np.log(1 / (1 + bg["z"]))
    hubble = np.exp(
        scipy.interpolate.interp1d(loga_bg, np.log(bg["H [1/Mpc]"]), kind="cubic")(loga)
    )
    rho = {}
    p = {}
    for s in species_unique:
        rho[s] = np.exp(
            scipy.interpolate.interp1d(loga_bg, np.log(bg[f"(.)rho_{s}"]), kind="cubic")(loga)
        )
        if s in ["b", "cdm"]:
            p[s] = 0
        elif s in ["g", "ur"]:
            p[s] = 1 / 3 * rho[s]
        elif s in ["fld"]:
            p[s] = rho[s] * scipy.interpolate.interp1d(
                loga_bg, bg[f"(.)w_{s}"], kind="cubic"
            )(loga)
        else:
            p[s] = np.exp(
                scipy.interpolate.interp1d(
                    loga_bg, np.log(bg[f"(.)p_{s}"]), kind="cubic"
                )(loga)
            )
    w = {s: p[s] / rho[s] for s in species_unique}
    # Interpolate perturbations in time
    delta = {s: np.empty(modes.size) for s in species_unique}
    theta_tot = np.empty(modes.size)
    for k, pt in enumerate(pts):
        loga_pt = np.log(pt["a"])
        mask = np.ones(loga_pt.size, dtype=bool)
        for i in range(1, loga_pt.size):
            mask[i] = loga_pt[i] != loga_pt[i - 1]
        loga_pt = loga_pt[mask]
        theta_tot[k] = (
            np.exp(
                scipy.interpolate.interp1d(
                    loga_pt, np.log(pt["theta_tot"][mask] ** 2), kind="cubic"
                )(loga)
            )
            ** 0.5
        )
        for s in species_unique:
            delta[s][k] = (
                np.exp(
                    scipy.interpolate.interp1d(
                        loga_pt, np.log(pt[f"delta_{s}"][mask] ** 2), kind="cubic"
                    )(loga)
                )
                ** 0.5
            )
            # Transform from synchronous to N-body gauge if required
            if gauge == "nbody":
                delta[s][k] += 3 * a * hubble * (1 + w[s]) * theta_tot[k] / modes[k] ** 2
    # Compute combined power spectrum
    delta_rho_combi = 0
    rho_combi = 0
    for s in split_species(species):
        delta_rho_combi += delta[s] * rho[s]
        rho_combi += rho[s]
    delta_combi = delta_rho_combi / rho_combi
    zeta = get_primordial_curvature_perturbation(params, modes)
    power_combi = (delta_combi * zeta) ** 2
    print(params)
    return modes, power_combi

