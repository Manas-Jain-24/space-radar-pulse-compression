"""Measurements of isolated, noise-free compressed waveforms."""
import numpy as np
from scipy.signal import find_peaks, peak_widths


def waveform_metrics(response, range_spacing_m):
    """Return sampled PSL and interpolated half-power width.

    PSL is the largest local maximum other than the central peak, not the
    noise floor of a target-plus-noise range profile.
    """
    power = np.abs(response) ** 2
    peak = int(np.argmax(power))
    peaks, _ = find_peaks(power)
    sidelobes = peaks[peaks != peak]
    psl = 10 * np.log10(np.max(power[sidelobes]) / power[peak]) if len(sidelobes) else float("nan")
    # Explicit zero baseline makes rel_height=0.5 a half-power crossing.
    prominence = np.array([power[peak]])
    bases = (np.array([0]), np.array([len(power) - 1]))
    width = peak_widths(power, [peak], rel_height=0.5,
                        prominence_data=(prominence, *bases))[0][0]
    return {"psl_db": float(psl), "half_power_width_m": float(width * range_spacing_m)}
