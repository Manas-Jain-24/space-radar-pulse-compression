"""Track 1: Radar Signal Processing — Target Detection, Pulse Compression & SNR Enhancement.

Curated by Mr. Rajendra Kumar, Scientist, Radar Division, SDSC SHAR.
Event: Beyond the Signal Research-athon (Utkrishta 2026, IIIT Sri City).

This module implements a complete, end-to-end LFM radar simulation chain:
1. PRT & Pulse Train Generation (PRT = 2 ms, tau = 10 us vs 100 us).
2. LFM Up-Chirp Generation (B = 4 MHz, time waveforms, instantaneous freq, spectra).
3. Radar Range Equation & Target Modeling (R = 200 km, RCS = 1 m^2, Pt = 250 kW).
4. Pulse Compression & Quantitative SNR Verification (+10 dB enhancement).
5. CA-CFAR Adaptive Thresholding & Link Margin Analysis.
"""

from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import matplotlib.pyplot as plt
import artifact_io
from scipy.fft import fft, ifft, fftshift, fftfreq, next_fast_len
from scipy.optimize import brentq
from scipy.stats import ncx2

# ==============================================================================
# 1. RADAR SYSTEM & TARGET PARAMETERS (HACKATHON TRACK 1 SPECIFICATIONS)
# ==============================================================================
C = 3.0e8                        # Speed of light (m/s)
FC = 3.0e9                       # Carrier frequency (Hz), S-band space-tracking radar
LAMBDA_C = C / FC                # Radar wavelength (0.10 m)
B = 4.0e6                        # Chirp sweep bandwidth (Hz) = 4 MHz
DELTA_R = C / (2 * B)            # Nominal range resolution = 37.5 m

PRT = 2.0e-3                     # Pulse Repetition Time (s) = 2.0 ms
PRF = 1.0 / PRT                  # Pulse Repetition Frequency = 500 Hz
R_UNAMB = C * PRT / 2            # Maximum unambiguous range = 300 km

TAU_1 = 10.0e-6                  # Pulse width 1 (s) = 10 us
TAU_2 = 100.0e-6                 # Pulse width 2 (s) = 100 us

R_TARGET = 200.0e3               # Point target range (m) = 200 km
TAU_DELAY = 2 * R_TARGET / C     # Round-trip delay (s) = 1.3333 ms
RCS = 1.0                        # Radar cross section (m^2) = 1 m^2 (0 dBsm)
VR_TARGET = 0.0                  # Radial velocity (m/s)

# Assumed S-band radar link parameters; not verified SDSC SHAR specifications.
PT = 250.0e3                     # Transmit peak power (W) = 250 kW
G_TX_DB = 40.0                   # Transmit antenna gain (dB)
G_RX_DB = 40.0                   # Receive antenna gain (dB)
G_TX = 10 ** (G_TX_DB / 10)
G_RX = 10 ** (G_RX_DB / 10)
NF_DB = 2.5                      # Receiver noise figure (dB)
NF = 10 ** (NF_DB / 10)
LOSS_DB = 3.0                    # Two-way atmospheric & system losses (dB)
LOSS = 10 ** (LOSS_DB / 10)
T0 = 290.0                       # Standard noise reference temperature (K)
K_B = 1.380649e-23               # Boltzmann constant (J/K)

# Sampling parameters: fs = 4 * B = 16 MHz ensures alias-free baseband processing
FS = 4 * B                       # Sampling frequency = 16 MHz
DT = 1.0 / FS                    # Sampling period = 62.5 ns
SAMPLE_SPACING = C / (2 * FS)    # Range bin spacing = 9.375 m
N_PRI = int(round(PRT * FS))     # Samples per PRI = 32,000 samples

# Detection criteria
PFA = 1.0e-6                     # Probability of false alarm
PD_TARGET = 0.90                 # Desired probability of detection


# ==============================================================================
# 2. CORE SIGNAL PROCESSING FUNCTIONS
# ==============================================================================

def generate_lfm_chirp(tau, b, fs):
    """Generate complex baseband LFM up-chirp centered at t=0 (-tau/2 to +tau/2)."""
    n_samples = int(round(tau * fs))
    t = (np.arange(n_samples) - (n_samples - 1) / 2) * (1.0 / fs)
    kr = b / tau  # Chirp slope (Hz/s)
    # Up-chirp: phase = pi * kr * t^2 -> instantaneous frequency sweeps from -B/2 to +B/2
    waveform = np.exp(1j * np.pi * kr * t**2)
    return t, waveform, kr


def compute_radar_link(pt, g_tx, g_rx, lambda_val, rcs, r_target, loss, nf, b, fs):
    """Calculate received target power and noise floor via the Radar Range Equation."""
    # Monostatic Radar Range Equation
    pr = (pt * g_tx * g_rx * (lambda_val**2) * rcs) / (((4 * np.pi)**3) * (r_target**4) * loss)
    n0 = K_B * T0 * nf                    # Noise power spectral density (W/Hz)
    pn_band = n0 * b                      # Noise power in matched bandwidth B (W)
    pn_sampled = n0 * fs                  # Total discrete-time noise variance (W)
    snr_in_band = pr / pn_band            # Uncompressed input SNR in bandwidth B
    return {
        "Pr": pr,
        "N0": n0,
        "Pn_band": pn_band,
        "Pn_sampled": pn_sampled,
        "SNR_in_band_dB": 10 * np.log10(snr_in_band),
        "A_target": np.sqrt(pr)
    }


def simulate_rx_echo(tau, b, fs, pr, r_target, n_pri, rng):
    """Construct causal received target echo with complex AWGN in one PRI."""
    dt = 1.0 / fs
    tau_delay = 2 * r_target / C
    t_pri = np.arange(n_pri) * dt
    
    # Check echo fits inside PRI
    if tau_delay + tau > PRT:
        raise ValueError("Echo exceeds PRI window!")

    # Chirp samples
    n_pulse = int(round(tau * fs))
    kr = b / tau
    t_pulse = np.arange(n_pulse) * dt - tau / 2
    s_tx = np.exp(1j * np.pi * kr * t_pulse**2)

    # Fractional delay positioning
    delay_sample_start = int(np.floor(tau_delay * fs))
    s_echo = np.zeros(n_pri, dtype=complex)
    
    # Calculate exact phase delay
    t_in_echo = t_pri[delay_sample_start:delay_sample_start + n_pulse] - tau_delay - tau / 2
    a_target = np.sqrt(pr)
    s_echo[delay_sample_start:delay_sample_start + n_pulse] = a_target * np.exp(1j * np.pi * kr * t_in_echo**2)
    
    # Complex AWGN with variance Pn_sampled = N0 * fs
    nf_val = 10 ** (NF_DB / 10)
    pn_sampled = K_B * T0 * nf_val * fs
    sigma_noise = np.sqrt(pn_sampled / 2)
    noise = sigma_noise * (rng.standard_normal(n_pri) + 1j * rng.standard_normal(n_pri))
    
    s_rx = s_echo + noise
    return s_tx, s_echo, noise, s_rx, pn_sampled


def matched_filter(rx_data, ref_pulse):
    """Zero-padded linear cross-correlation (matched filter) via FFT."""
    n_rx = len(rx_data)
    n_ref = len(ref_pulse)
    n_fft = next_fast_len(n_rx + n_ref - 1)
    
    # Matched filter transfer function: conj(FFT(ref))
    y_full = ifft(fft(rx_data, n_fft) * np.conj(fft(ref_pulse, n_fft)))
    # Valid causal overlap
    y_mf = y_full[:n_rx]
    return y_mf


def measure_mainlobe_and_psl(y_power, range_axis, r_target, search_window_m=500.0):
    """Measure -3 dB (half-power) mainlobe width and peak sidelobe level (PSL)."""
    mask = np.abs(range_axis - r_target) <= search_window_m
    sub_r = range_axis[mask]
    sub_p = y_power[mask]
    
    peak_idx = np.argmax(sub_p)
    peak_val = sub_p[peak_idx]
    peak_r = sub_r[peak_idx]
    half_val = peak_val / 2.0  # -3 dB in power
    
    # Left 3dB point
    left_idx = peak_idx
    while left_idx > 0 and sub_p[left_idx] > half_val:
        left_idx -= 1
    # Interpolate
    if left_idx < peak_idx and sub_p[left_idx] <= half_val:
        r_left = np.interp(half_val, [sub_p[left_idx], sub_p[left_idx + 1]], [sub_r[left_idx], sub_r[left_idx + 1]])
    else:
        r_left = sub_r[left_idx]
        
    # Right 3dB point
    right_idx = peak_idx
    while right_idx < len(sub_p) - 1 and sub_p[right_idx] > half_val:
        right_idx += 1
    if right_idx > peak_idx and sub_p[right_idx] <= half_val:
        r_right = np.interp(half_val, [sub_p[right_idx], sub_p[right_idx - 1]], [sub_r[right_idx], sub_r[right_idx - 1]])
    else:
        r_right = sub_r[right_idx]
        
    mainlobe_width_m = abs(r_right - r_left)
    
    # Sidelobe measurement outside mainlobe
    null_exclusion = max(mainlobe_width_m * 1.2, 50.0)
    sidelobe_mask = np.abs(sub_r - peak_r) > null_exclusion
    if np.any(sidelobe_mask):
        peak_sidelobe = np.max(sub_p[sidelobe_mask])
        psl_db = 10 * np.log10(peak_sidelobe / peak_val + 1e-30)
    else:
        psl_db = -13.2
        
    return peak_r, mainlobe_width_m, psl_db


def ca_cfar(power, n_ref=24, n_guard=8, pfa=1e-6):
    """1D Cell-Averaging CFAR detector on power profile."""
    n_ref_total = 2 * n_ref
    # Analytic multiplier for exponential/Rayleigh noise: alpha = N * (Pfa^(-1/N) - 1)
    alpha = n_ref_total * (pfa ** (-1.0 / n_ref_total) - 1.0)
    threshold = np.full_like(power, np.nan)
    
    valid_start = n_guard + n_ref
    valid_end = len(power) - (n_guard + n_ref)
    
    cumsum = np.concatenate(([0.0], np.cumsum(power)))
    indices = np.arange(valid_start, valid_end)
    
    left_sum = cumsum[indices - n_guard] - cumsum[indices - n_guard - n_ref]
    right_sum = cumsum[indices + n_guard + n_ref + 1] - cumsum[indices + n_guard + 1]
    
    threshold[indices] = alpha * (left_sum + right_sum) / n_ref_total
    detections = power > threshold
    return threshold, detections, alpha


def marcum_q1(a, b):
    """Marcum Q-function for Swerling 0 detection probability."""
    return ncx2.sf(b**2, df=2, nc=a**2)


def monte_carlo_snr(n_trials=200):
    """Exercise the production echo/filter path using paired noise realizations.

    The peak statistic uses the known output noise variance, as in the main run.
    The interval describes the mean gain, not detection probability.
    """
    if n_trials < 2:
        raise ValueError("At least two trials are required")
    link = compute_radar_link(PT, G_TX, G_RX, LAMBDA_C, RCS, R_TARGET, LOSS, NF, B, FS)
    mask = np.abs(np.arange(N_PRI) * SAMPLE_SPACING - R_TARGET) <= 500
    boosts = []
    for seed in range(n_trials):
        rng = np.random.default_rng(seed)
        noise = None
        peaks = []
        for tau in (TAU_1, TAU_2):
            tx, echo, ns, _, pn = simulate_rx_echo(tau, B, FS, link["Pr"], R_TARGET, N_PRI, rng)
            if noise is None:
                noise = ns
            power = np.abs(matched_filter(echo + noise, tx)) ** 2
            peaks.append(10 * np.log10(np.max(power[mask]) / (pn * np.sum(np.abs(tx) ** 2))))
        boosts.append(peaks[1] - peaks[0])
    mean = float(np.mean(boosts))
    std = float(np.std(boosts, ddof=1))
    half_ci = 1.96 * std / np.sqrt(n_trials)
    return {"n_trials": n_trials, "mean_boost_db": mean, "std_boost_db": std,
            "mean_ci95_db": [float(mean - half_ci), float(mean + half_ci)]}


# ==============================================================================
# 3. MAIN SIMULATION & VISUALIZATION PIPELINE
# ==============================================================================

def run_simulation(output_dir="figures/track1", show=False):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026)  # Seed for reproducible research results

    print("=" * 80)
    print("UTKRISHTA 2026 - BEYOND THE SIGNAL RESEARCH-ATHON")
    print("TRACK 1: LFM RADAR PULSE COMPRESSION & +10 dB SNR ENHANCEMENT SIMULATION")
    print("Curated by: Mr. Rajendra Kumar (Scientist, Radar Division, SDSC SHAR)")
    print("=" * 80)

    # Calculate Link Budget
    link = compute_radar_link(PT, G_TX, G_RX, LAMBDA_C, RCS, R_TARGET, LOSS, NF, B, FS)
    pr = link["Pr"]
    n0 = link["N0"]
    pn_band = link["Pn_band"]
    pn_sampled = link["Pn_sampled"]

    # Compute Theoretical Metrics
    # Pulse 1: 10 us
    tb_1 = B * TAU_1
    tb_1_db = 10 * np.log10(tb_1)
    kr_1 = B / TAU_1
    snr_ideal_1 = (pr * TAU_1) / n0
    snr_ideal_1_db = 10 * np.log10(snr_ideal_1)

    # Pulse 2: 100 us
    tb_2 = B * TAU_2
    tb_2_db = 10 * np.log10(tb_2)
    kr_2 = B / TAU_2
    snr_ideal_2 = (pr * TAU_2) / n0
    snr_ideal_2_db = 10 * np.log10(snr_ideal_2)

    delta_snr_theory_db = snr_ideal_2_db - snr_ideal_1_db

    # Detection threshold for Swerling 0 (Pfa = 1e-6, Pd = 0.90)
    b_thresh = np.sqrt(-2 * np.log(PFA))
    snr_req_db = brentq(lambda x: marcum_q1(np.sqrt(2 * 10**(x / 10)), b_thresh) - PD_TARGET, -10, 40)
    margin_1_db = snr_ideal_1_db - snr_req_db
    margin_2_db = snr_ideal_2_db - snr_req_db

    print(f"\n[1] RADAR LINK BUDGET & THEORETICAL VALUES (Target R = {R_TARGET/1e3:.0f} km, RCS = {RCS:.1f} m^2):")
    print(f"  Transmit Peak Power (Pt)   : {PT/1e3:.1f} kW ({10*np.log10(PT):.2f} dBW)")
    print(f"  Antenna Gain (Tx & Rx)     : {G_TX_DB:.1f} dBi each")
    print(f"  Carrier / Bandwidth (fc, B): {FC/1e9:.2f} GHz (S-band) | {B/1e6:.1f} MHz")
    print(f"  Noise Figure / Loss (F, L) : {NF_DB:.1f} dB | {LOSS_DB:.1f} dB")
    print(f"  Received Power (Pr)        : {pr:.4e} W ({10*np.log10(pr):.2f} dBW / {10*np.log10(pr*1e3):.2f} dBm)")
    print(f"  Noise Spectral Density (N0): {n0:.4e} W/Hz ({10*np.log10(n0):.2f} dBW/Hz)")
    print(f"  In-Band Noise Power (Pn)   : {pn_band:.4e} W ({10*np.log10(pn_band):.2f} dBW)")
    print(f"  Raw Input SNR in Band B    : {link['SNR_in_band_dB']:.2f} dB")
    print(f"  Sampled Noise Power (fs)   : {pn_sampled:.4e} W")
    print(f"\n[2] DUAL-PULSE COMPARATIVE METRICS:")
    print(f"  Metric                     | Pulse 1 (10 us)       | Pulse 2 (100 us)      | Difference")
    print(f"  ---------------------------+-----------------------+-----------------------+-------------------")
    print(f"  Pulse Duration (tau)       | {TAU_1*1e6:7.1f} us          | {TAU_2*1e6:7.1f} us          | x10.0 (+10 dB)")
    print(f"  Duty Cycle (tau / PRT)     | {TAU_1/PRT*100:7.2f} %           | {TAU_2/PRT*100:7.2f} %           | x10.0")
    print(f"  Pulse Energy (Pt * tau)    | {PT*TAU_1:7.2f} J            | {PT*TAU_2:7.2f} J            | +10.0 dB")
    print(f"  Chirp Slope (kr = B / tau) | {kr_1:7.2e} Hz/s       | {kr_2:7.2e} Hz/s       | 1/10")
    print(f"  Time-Bandwidth Product (TB)| {tb_1:7.1f} ({tb_1_db:4.1f} dB)    | {tb_2:7.1f} ({tb_2_db:4.1f} dB)   | +10.0 dB")
    print(f"  Ideal Matched-Filter SNR   | {snr_ideal_1_db:7.2f} dB           | {snr_ideal_2_db:7.2f} dB           | {delta_snr_theory_db:+5.2f} dB")
    print(f"  Required SNR (Pd=0.9, Pfa) | {snr_req_db:7.2f} dB           | {snr_req_db:7.2f} dB           | --")
    print(f"  Theoretical Link Margin    | {margin_1_db:7.2f} dB           | {margin_2_db:7.2f} dB           | {margin_2_db - margin_1_db:+5.2f} dB")
    print(f"  Nominal Range Resolution   | {DELTA_R:7.2f} m            | {DELTA_R:7.2f} m            | IDENTICAL!")

    # --------------------------------------------------------------------------
    # TASK 1 & 2: GENERATE SIGNALS, SPECTRA & PULSE TRAIN
    # --------------------------------------------------------------------------
    t_chirp_1, chirp_1, _ = generate_lfm_chirp(TAU_1, B, FS)
    t_chirp_2, chirp_2, _ = generate_lfm_chirp(TAU_2, B, FS)

    # Plot 1: PRT & Pulse Train Comparison
    t_train = np.arange(int(round(2 * PRT * FS))) / FS
    train_1 = np.zeros_like(t_train)
    train_2 = np.zeros_like(t_train)
    
    # Pulse train repetition
    n_p1 = int(round(TAU_1 * FS))
    n_p2 = int(round(TAU_2 * FS))
    n_prt = int(round(PRT * FS))
    for p_idx in range(2):
        train_1[p_idx * n_prt : p_idx * n_prt + n_p1] = 1.0
        train_2[p_idx * n_prt : p_idx * n_prt + n_p2] = 1.0

    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    ax1.plot(t_train * 1e3, train_1, color="#1f77b4", lw=1.2, label=r"$\tau_1 = 10\ \mu\mathrm{s}$ (Duty Cycle = 0.5%)")
    ax1.set_title(r"Radar Pulse Train: Pulse Repetition Time ($\mathrm{PRT} = 2.0\ \mathrm{ms}$, $\mathrm{PRF} = 500\ \mathrm{Hz}$)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Normalized Amplitude", fontsize=11)
    ax1.set_ylim(-0.1, 1.3)
    ax1.grid(True, alpha=0.3, ls="--")
    ax1.legend(loc="upper right", framealpha=0.9, fontsize=10)

    ax2.plot(t_train * 1e3, train_2, color="#d62728", lw=1.2, label=r"$\tau_2 = 100\ \mu\mathrm{s}$ (Duty Cycle = 5.0%)")
    ax2.set_xlabel("Time (ms)", fontsize=11)
    ax2.set_ylabel("Normalized Amplitude", fontsize=11)
    ax2.set_ylim(-0.1, 1.3)
    ax2.grid(True, alpha=0.3, ls="--")
    ax2.legend(loc="upper right", framealpha=0.9, fontsize=10)
    fig1.tight_layout()
    artifact_io.save_figure(fig1, out_path / "fig1_prt_pulse_train.png", dpi=300)
    print(f"\n[Generated] {out_path / 'fig1_prt_pulse_train.png'}")

    # Plot 2: Time-Domain Waveforms & Frequency Spectra
    n_fft_spec = 4096
    freq_axis = fftshift(fftfreq(n_fft_spec, d=DT)) / 1e6  # MHz
    spec_1 = fftshift(fft(chirp_1, n_fft_spec))
    spec_2 = fftshift(fft(chirp_2, n_fft_spec))
    spec_1_db = 20 * np.log10(np.abs(spec_1) / np.max(np.abs(spec_1)) + 1e-12)
    spec_2_db = 20 * np.log10(np.abs(spec_2) / np.max(np.abs(spec_2)) + 1e-12)

    fig2, axes2 = plt.subplots(2, 2, figsize=(14, 8))
    # Time domain real part
    axes2[0, 0].plot(t_chirp_1 * 1e6, chirp_1.real, color="#1f77b4", lw=0.9)
    axes2[0, 0].set_title(r"LFM Up-Chirp: $\tau_1 = 10\ \mu\mathrm{s},\ B = 4\ \mathrm{MHz}\ (k_r = 4\times 10^{11}\ \mathrm{Hz/s})$", fontsize=11, fontweight="bold")
    axes2[0, 0].set_xlabel(r"Local Time ($\mu\mathrm{s}$)", fontsize=10)
    axes2[0, 0].set_ylabel("In-Phase Amplitude", fontsize=10)
    axes2[0, 0].grid(True, alpha=0.3)

    axes2[0, 1].plot(t_chirp_2 * 1e6, chirp_2.real, color="#d62728", lw=0.7)
    axes2[0, 1].set_title(r"LFM Up-Chirp: $\tau_2 = 100\ \mu\mathrm{s},\ B = 4\ \mathrm{MHz}\ (k_r = 4\times 10^{10}\ \mathrm{Hz/s})$", fontsize=11, fontweight="bold")
    axes2[0, 1].set_xlabel(r"Local Time ($\mu\mathrm{s}$)", fontsize=10)
    axes2[0, 1].set_ylabel("In-Phase Amplitude", fontsize=10)
    axes2[0, 1].grid(True, alpha=0.3)

    # Frequency Spectra
    axes2[1, 0].plot(freq_axis, spec_1_db, color="#1f77b4", lw=1.2)
    axes2[1, 0].axvline(-B / 2e6, color="black", ls="--", lw=1.0, label=r"$-B/2 = -2.0\ \mathrm{MHz}$")
    axes2[1, 0].axvline(B / 2e6, color="black", ls="--", lw=1.0, label=r"$+B/2 = +2.0\ \mathrm{MHz}$")
    axes2[1, 0].set_title(r"Normalized Spectrum: $\tau_1 = 10\ \mu\mathrm{s}\ (TB = 40)$", fontsize=11, fontweight="bold")
    axes2[1, 0].set_xlabel("Baseband Frequency (MHz)", fontsize=10)
    axes2[1, 0].set_ylabel("Normalized Magnitude (dB)", fontsize=10)
    axes2[1, 0].set_xlim(-4, 4)
    axes2[1, 0].set_ylim(-40, 2)
    axes2[1, 0].grid(True, alpha=0.3)
    axes2[1, 0].legend(loc="lower right", fontsize=9)

    axes2[1, 1].plot(freq_axis, spec_2_db, color="#d62728", lw=1.2)
    axes2[1, 1].axvline(-B / 2e6, color="black", ls="--", lw=1.0, label=r"$-B/2 = -2.0\ \mathrm{MHz}$")
    axes2[1, 1].axvline(B / 2e6, color="black", ls="--", lw=1.0, label=r"$+B/2 = +2.0\ \mathrm{MHz}$")
    axes2[1, 1].set_title(r"Normalized Spectrum: $\tau_2 = 100\ \mu\mathrm{s}\ (TB = 400)$ [Steeper Roll-off]", fontsize=11, fontweight="bold")
    axes2[1, 1].set_xlabel("Baseband Frequency (MHz)", fontsize=10)
    axes2[1, 1].set_ylabel("Normalized Magnitude (dB)", fontsize=10)
    axes2[1, 1].set_xlim(-4, 4)
    axes2[1, 1].set_ylim(-40, 2)
    axes2[1, 1].grid(True, alpha=0.3)
    axes2[1, 1].legend(loc="lower right", fontsize=9)

    fig2.suptitle("LFM Chirp Generation: Time Waveforms & Baseband Spectra (Bandwidth = 4.0 MHz)", fontsize=13, fontweight="bold")
    fig2.tight_layout()
    artifact_io.save_figure(fig2, out_path / "fig2_lfm_waveforms_and_spectra.png", dpi=300)
    print(f"[Generated] {out_path / 'fig2_lfm_waveforms_and_spectra.png'}")

    # --------------------------------------------------------------------------
    # TASK 3: SIMULATE NOISY TARGET ECHOES AT R = 200 KM
    # --------------------------------------------------------------------------
    s_tx1, s_echo1, noise1, s_rx1, _ = simulate_rx_echo(TAU_1, B, FS, pr, R_TARGET, N_PRI, rng)
    # Use identical noise realization for a 100% fair and rigorous scientific comparison
    s_tx2, s_echo2, _, s_rx2, _ = simulate_rx_echo(TAU_2, B, FS, pr, R_TARGET, N_PRI, rng)
    s_rx2 = s_echo2 + noise1  # exact same noise realization

    t_pri_ms = (np.arange(N_PRI) * DT) * 1e3
    range_axis_km = (np.arange(N_PRI) * C / (2 * FS)) / 1e3

    fig3, (ax3a, ax3b) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    rx1_env_dbm = 10 * np.log10(np.abs(s_rx1)**2 * 1e3 + 1e-16)
    rx2_env_dbm = 10 * np.log10(np.abs(s_rx2)**2 * 1e3 + 1e-16)

    ax3a.plot(range_axis_km, rx1_env_dbm, color="slategray", lw=0.6, label="Received Signal (Echo + AWGN)")
    ax3a.axvline(R_TARGET / 1e3, color="#1f77b4", ls="--", lw=1.5, label=f"Target Echo (R = 200 km, delay = {TAU_DELAY*1e3:.2f} ms)")
    ax3a.set_title(r"Raw Received Signal at Receiver: $\tau_1 = 10\ \mu\mathrm{s}$ (Completely Buried in Noise Floor)", fontsize=11, fontweight="bold")
    ax3a.set_ylabel("Power (dBm)", fontsize=10)
    ax3a.grid(True, alpha=0.3)
    ax3a.legend(loc="upper right", fontsize=9)

    ax3b.plot(range_axis_km, rx2_env_dbm, color="dimgray", lw=0.6, label="Received Signal (Echo + AWGN)")
    ax3b.axvline(R_TARGET / 1e3, color="#d62728", ls="--", lw=1.5, label=f"Target Echo (R = 200 km, delay = {TAU_DELAY*1e3:.2f} ms)")
    ax3b.set_title(r"Raw Received Signal at Receiver: $\tau_2 = 100\ \mu\mathrm{s}$ (10x Energy, Still Sub-Noise)", fontsize=11, fontweight="bold")
    ax3b.set_xlabel("Range (km)", fontsize=10)
    ax3b.set_ylabel("Power (dBm)", fontsize=10)
    ax3b.grid(True, alpha=0.3)
    ax3b.legend(loc="upper right", fontsize=9)

    fig3.suptitle("Target Echo at 200 km: Radar Range Equation & Receiver Noise Floor", fontsize=13, fontweight="bold")
    fig3.tight_layout()
    artifact_io.save_figure(fig3, out_path / "fig3_target_echo_at_200km.png", dpi=300)
    print(f"[Generated] {out_path / 'fig3_target_echo_at_200km.png'}")

    # --------------------------------------------------------------------------
    # TASK 4: PULSE COMPRESSION & +10 dB SNR VERIFICATION
    # --------------------------------------------------------------------------
    # Matched filter
    y_mf1 = matched_filter(s_rx1, s_tx1)
    y_mf2 = matched_filter(s_rx2, s_tx2)

    # Power profiles
    # Matched filter output noise variance scaling:
    # Var(y_noise) = Pn_sampled * sum(|s_tx|^2) = (N0 * fs) * N_pulse = N0 * fs * (tau * fs) = N0 * tau * fs^2
    noise_var_out1 = pn_sampled * np.sum(np.abs(s_tx1)**2)
    noise_var_out2 = pn_sampled * np.sum(np.abs(s_tx2)**2)

    # Normalize matched filter output power to output noise variance (SNR units)
    p_mf1_snr = np.abs(y_mf1)**2 / noise_var_out1
    p_mf2_snr = np.abs(y_mf2)**2 / noise_var_out2

    p_mf1_snr_db = 10 * np.log10(p_mf1_snr + 1e-12)
    p_mf2_snr_db = 10 * np.log10(p_mf2_snr + 1e-12)

    # Measure measured empirical metrics at target peak
    range_axis_m = np.arange(len(y_mf1)) * (C / (2 * FS))
    peak_r1, mlw_1, psl_1_db = measure_mainlobe_and_psl(p_mf1_snr, range_axis_m, R_TARGET)
    peak_r2, mlw_2, psl_2_db = measure_mainlobe_and_psl(p_mf2_snr, range_axis_m, R_TARGET)

    # Measured empirical peak SNR
    peak_idx1 = int(round(peak_r1 / (C / (2 * FS))))
    peak_idx2 = int(round(peak_r2 / (C / (2 * FS))))
    snr_meas_1_db = p_mf1_snr_db[peak_idx1]
    snr_meas_2_db = p_mf2_snr_db[peak_idx2]
    delta_snr_meas_db = snr_meas_2_db - snr_meas_1_db

    print(f"\n[3] EMPIRICAL PULSE COMPRESSION & SNR ENHANCEMENT RESULTS:")
    print(f"  Pulse 1 (tau = 10 us)  : Peak SNR = {snr_meas_1_db:6.2f} dB | Half-Power Width = {mlw_1:5.2f} m | PSL = {psl_1_db:5.2f} dB")
    print(f"  Pulse 2 (tau = 100 us) : Peak SNR = {snr_meas_2_db:6.2f} dB | Half-Power Width = {mlw_2:5.2f} m | PSL = {psl_2_db:5.2f} dB")
    print(f"  ==========================================================================")
    print(f"  MEASURED SNR ENHANCEMENT (tau=100 us vs tau=10 us): {delta_snr_meas_db:+6.2f} dB  (Theory: +10.00 dB)")
    print(f"  MEASURED MAINLOBE WIDTH RATIO                     : {mlw_2 / mlw_1:6.2f}x   (Theory: 1.00x - Identical Resolution)")
    print(f"  ==========================================================================")

    # Plot 4: Pulse Compression & +10 dB SNR Verification
    fig4, axes4 = plt.subplots(2, 1, figsize=(13, 9))
    
    # 4a: Full range profile 0 to 300 km
    axes4[0].plot(range_axis_m / 1e3, p_mf1_snr_db, color="#1f77b4", lw=0.7, alpha=0.8, label=r"$\tau_1 = 10\ \mu\mathrm{s}$ (MF Output)")
    axes4[0].plot(range_axis_m / 1e3, p_mf2_snr_db, color="#d62728", lw=0.7, alpha=0.8, label=r"$\tau_2 = 100\ \mu\mathrm{s}$ (MF Output)")
    axes4[0].axvline(R_TARGET / 1e3, color="green", ls="--", lw=1.2, label="Target (200 km)")
    threshold_stat_db = 10 * np.log10(-np.log(PFA))
    axes4[0].axhline(threshold_stat_db, color="darkorange", ls=":", lw=1.5,
                    label=f"Known-noise power threshold ({threshold_stat_db:.1f} dB; Pfa={PFA:g})")
    axes4[0].set_title("Full Unambiguous Range Profile (0 to 300 km)", fontsize=11, fontweight="bold")
    axes4[0].set_xlabel("Range (km)", fontsize=10)
    axes4[0].set_ylabel("Output SNR (dB)", fontsize=10)
    axes4[0].set_ylim(-15, 35)
    axes4[0].grid(True, alpha=0.3)
    axes4[0].legend(loc="upper right", fontsize=9)

    # 4b: Zoom around 200 km target (+- 350 m)
    zoom_mask = np.abs(range_axis_m - R_TARGET) <= 350.0
    r_zoom_offset = range_axis_m[zoom_mask] - R_TARGET

    axes4[1].plot(r_zoom_offset, p_mf1_snr_db[zoom_mask], color="#1f77b4", marker="o", ms=4, lw=1.5,
                  label=rf"$\tau_1 = 10\ \mu\mathrm{{s}}$: Peak SNR = {snr_meas_1_db:.2f} dB, $\Delta R_{{-3\mathrm{{dB}}}} = {mlw_1:.1f}\ \mathrm{{m}}$")
    axes4[1].plot(r_zoom_offset, p_mf2_snr_db[zoom_mask], color="#d62728", marker="s", ms=4, lw=1.5,
                  label=rf"$\tau_2 = 100\ \mu\mathrm{{s}}$: Peak SNR = {snr_meas_2_db:.2f} dB, $\Delta R_{{-3\mathrm{{dB}}}} = {mlw_2:.1f}\ \mathrm{{m}}$")
    axes4[1].axvline(0, color="gray", ls=":", lw=1.0)
    axes4[1].axhline(snr_meas_1_db, color="#1f77b4", ls="--", lw=0.8)
    axes4[1].axhline(snr_meas_2_db, color="#d62728", ls="--", lw=0.8)

    # Annotation for +10 dB boost
    axes4[1].annotate(
        "", xy=(150, snr_meas_2_db), xytext=(150, snr_meas_1_db),
        arrowprops=dict(arrowstyle="<->", color="purple", lw=2.0)
    )
    axes4[1].text(165, (snr_meas_1_db + snr_meas_2_db) / 2,
                 rf"$\mathbf{{\Delta \mathrm{{SNR}} = {delta_snr_meas_db:+.2f}\ \mathrm{{dB}}}}$" "\n(Theoretical: +10.00 dB)",
                 color="purple", fontsize=11, fontweight="bold", va="center")

    axes4[1].set_title(r"Zoomed Compressed Target Echo at $R = 200\ \mathrm{km}$: Visual & Quantitative +10 dB Proof", fontsize=11, fontweight="bold")
    axes4[1].set_xlabel("Range Offset from Target (m)", fontsize=10)
    axes4[1].set_ylabel("Output SNR (dB)", fontsize=10)
    axes4[1].set_ylim(-10, 35)
    axes4[1].grid(True, alpha=0.3)
    axes4[1].legend(loc="upper left", fontsize=10, framealpha=0.95)

    fig4.suptitle("Pulse Compression Verification: +10 dB SNR Enhancement with Identical Range Resolution", fontsize=13, fontweight="bold")
    fig4.tight_layout()
    artifact_io.save_figure(fig4, out_path / "fig4_pulse_compression_snr_boost.png", dpi=300)
    print(f"[Generated] {out_path / 'fig4_pulse_compression_snr_boost.png'}")

    # --------------------------------------------------------------------------
    # TASK 5: CA-CFAR DETECTION & LINK MARGIN
    # --------------------------------------------------------------------------
    thresh_1, det_1, alpha = ca_cfar(p_mf1_snr, n_ref=24, n_guard=8, pfa=PFA)
    thresh_2, det_2, _ = ca_cfar(p_mf2_snr, n_ref=24, n_guard=8, pfa=PFA)

    thresh_1_db = 10 * np.log10(thresh_1 + 1e-12)
    thresh_2_db = 10 * np.log10(thresh_2 + 1e-12)

    cfar_margin_1 = snr_meas_1_db - thresh_1_db[peak_idx1]
    cfar_margin_2 = snr_meas_2_db - thresh_2_db[peak_idx2]

    fig5, (ax5a, ax5b) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    zoom_cfar_mask = np.abs(range_axis_m / 1e3 - 200.0) <= 2.0  # +- 2 km around target
    r_cfar_km = range_axis_m[zoom_cfar_mask] / 1e3

    ax5a.plot(r_cfar_km, p_mf1_snr_db[zoom_cfar_mask], color="#1f77b4", lw=1.2, label=r"Power Profile ($\tau_1 = 10\ \mu\mathrm{s}$)")
    ax5a.plot(r_cfar_km, thresh_1_db[zoom_cfar_mask], color="orange", ls="--", lw=1.5, label=rf"CA-CFAR Threshold ($P_{{fa}}=10^{{-6}}$, Margin = {cfar_margin_1:.2f} dB)")
    ax5a.axvline(200.0, color="green", ls=":", lw=1.0)
    ax5a.set_title(r"Adaptive CA-CFAR: $\tau_1 = 10\ \mu\mathrm{s}$ (Marginal Target Detection)", fontsize=11, fontweight="bold")
    ax5a.set_ylabel("Power / SNR (dB)", fontsize=10)
    ax5a.grid(True, alpha=0.3)
    ax5a.legend(loc="upper right", fontsize=9)

    ax5b.plot(r_cfar_km, p_mf2_snr_db[zoom_cfar_mask], color="#d62728", lw=1.2, label=r"Power Profile ($\tau_2 = 100\ \mu\mathrm{s}$)")
    ax5b.plot(r_cfar_km, thresh_2_db[zoom_cfar_mask], color="orange", ls="--", lw=1.5, label=rf"CA-CFAR Threshold ($P_{{fa}}=10^{{-6}}$, Margin = {cfar_margin_2:.2f} dB)")
    ax5b.axvline(200.0, color="green", ls=":", lw=1.0)
    ax5b.set_title(r"Adaptive CA-CFAR: $\tau_2 = 100\ \mu\mathrm{s}$ (Measured Local Threshold)", fontsize=11, fontweight="bold")
    ax5b.set_xlabel("Range (km)", fontsize=10)
    ax5b.set_ylabel("Power / SNR (dB)", fontsize=10)
    ax5b.grid(True, alpha=0.3)
    ax5b.legend(loc="upper right", fontsize=9)

    fig5.suptitle("Adaptive CA-CFAR Detection: Target Detection Margin at Range = 200 km", fontsize=13, fontweight="bold")
    fig5.tight_layout()
    artifact_io.save_figure(fig5, out_path / "fig5_detection_and_cfar_margin.png", dpi=300)
    print(f"[Generated] {out_path / 'fig5_detection_and_cfar_margin.png'}")

    print("\n" + "=" * 80)
    print("ALL SIMULATION EXPERIMENTS COMPLETED SUCCESSFULLY!")
    print(f"All 5 publication-ready plots saved to: {out_path.resolve()}")
    print("=" * 80)

    results = {
        "snr_meas_1_db": snr_meas_1_db,
        "snr_meas_2_db": snr_meas_2_db,
        "delta_snr_meas_db": delta_snr_meas_db,
        "mlw_1": mlw_1,
        "mlw_2": mlw_2,
        "psl_1_db": psl_1_db,
        "psl_2_db": psl_2_db,
        "margin_1_db": margin_1_db,
        "margin_2_db": margin_2_db,
        "cfar_margin_1": cfar_margin_1,
        "cfar_margin_2": cfar_margin_2,
        "snr_theory_1_db": snr_ideal_1_db,
        "snr_theory_2_db": snr_ideal_2_db,
        "snr_required_db": snr_req_db,
        "nominal_resolution_m": DELTA_R,
        "seed": 2026,
        "cfar_reference_total": 48,
        "cfar_guard_total": 16,
        "monte_carlo": monte_carlo_snr(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "assumptions": "Synthetic nonfluctuating point target; assumed S-band link parameters. CA-CFAR nominal Pfa assumes independent exponential cells; oversampled MF cells are correlated."
    }
    with artifact_io.atomic_output(out_path / "simulation_results.json") as temporary:
        temporary.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"[Results] {out_path / 'simulation_results.json'}")
    if show:
        plt.show()
    else:
        plt.close("all")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track 1 LFM Radar Simulation")
    parser.add_argument("--output-dir", type=str, default="figures/track1", help="Output directory for plots")
    parser.add_argument("--show", action="store_true", help="Display plots interactively")
    args = parser.parse_args()
    run_simulation(output_dir=args.output_dir, show=args.show)
