"""
Advanced Radar Upgrade 2: Advanced CFAR Family Comparison
=========================================================
Beyond the Signal: Radar Systems & Applied Space-Tech Research-Athon (Utkrishta 2026)
Track 1: Radar Signal Processing (Curated by Mr. Rajendra Kumar, Scientist, SDSC SHAR, ISRO)

Theoretical Background:
-----------------------
Cell-Averaging CFAR (CA-CFAR) assumes a homogeneous, stationary noise background.
In real SDSC SHAR space launch tracking, two major non-homogeneous environments degrade CA-CFAR:

1. Multi-Target Masking (Cluster / Separation Scenario):
   When two space objects (e.g. rocket core and payload) are closely spaced, an interfering target
   falls into the reference window of the Cell Under Test (CUT).
   - CA-CFAR: The high interfering target energy inflates the noise estimate, raising the threshold
     and causing missed detection of the secondary target ("Target Masking").
   - SO-CFAR (Smallest-Of): Computes separate leading and lagging averages and selects the MINIMUM:
         P_hat_SO = min(P_lead, P_lag)
     Because the interfering target only corrupts one half-window, SO-CFAR ignores that half,
     preventing threshold inflation and resolving both targets cleanly!

2. Clutter Edges (Ground/Sea Clutter or Ionospheric Transition):
   When the antenna beam crosses a sharp clutter step (+15 dB to +20 dB):
   - CA-CFAR: Sets an intermediate threshold that is too low inside the clutter region, causing
     a catastrophic spike in False Alarm Rate (Pfa can increase; its value must be measured.).
   - GO-CFAR (Greatest-Of): Computes leading and lagging averages and selects the MAXIMUM:
         P_hat_GO = max(P_lead, P_lag)
     It immediately adopts the clutter level, maintaining tight false alarm regulation.

3. OS-CFAR (Ordered-Statistic):
   Ranks all reference cells X_(1) <= X_(2) <= ... <= X_(N) and selects the k-th ranked value
   (typically k = 3/4 * N). Provides robust immunity against multiple interfering targets.
"""

import os
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import artifact_io
from functools import lru_cache
from scipy.optimize import brentq
from scipy.special import gammaln


@lru_cache(maxsize=128)
def threshold_factor(method, n_train, pfa, rank=None):
    """Exact calibration for independent exponential power cells (unit mean).

    GO/SO use the Laplace transform of the max/min of two gamma means;
    OS uses the Laplace transform of the kth exponential order statistic.
    Correlated matched-filter cells require separate empirical validation.
    """
    if n_train < 1 or not 0 < pfa < 1:
        raise ValueError("Require positive training count and 0 < pfa < 1")
    n = n_train
    if method == "OS":
        total = 2 * n
        if rank is None or not 1 <= rank <= total:
            raise ValueError("OS rank must be between 1 and the reference count")
        rates = np.arange(total - rank + 1, total + 1, dtype=float)
        def probability(alpha):
            return np.exp(-np.log1p(alpha / rates).sum())
    elif method in ("GO", "SO"):
        j = np.arange(n)
        log_coeff = gammaln(n + j) - gammaln(n) - gammaln(j + 1)
        def probability(alpha):
            smallest = 2 * np.exp(log_coeff - (n + j) * np.log(2 + alpha / n)).sum()
            return smallest if method == "SO" else 2 * (1 + alpha / n) ** (-n) - smallest
    else:
        raise ValueError("Method must be GO, SO or OS")
    upper = 1.0
    while probability(upper) > pfa:
        upper *= 2
    return brentq(lambda alpha: probability(alpha) - pfa, 0, upper)

def compute_ca_cfar(power_signal, n_guard, n_train, pfa):
    """Standard Cell-Averaging CFAR"""
    N_ref = 2 * n_train
    alpha = N_ref * (pfa ** (-1.0 / N_ref) - 1.0)
    
    kernel = np.ones(2 * (n_train + n_guard) + 1)
    kernel[n_train : n_train + 2 * n_guard + 1] = 0.0
    kernel = kernel / N_ref
    
    noise_est = np.convolve(power_signal, kernel, mode='same')
    return alpha * noise_est

def compute_go_cfar(power_signal, n_guard, n_train, pfa):
    """Greatest-Of CFAR (Clutter Edge Specialist)"""
    N_half = n_train
    alpha = threshold_factor("GO", N_half, pfa)
    
    lead_kernel = np.zeros(2 * (n_train + n_guard) + 1)
    lead_kernel[:n_train] = 1.0 / n_train
    
    lag_kernel = np.zeros(2 * (n_train + n_guard) + 1)
    lag_kernel[n_train + 2 * n_guard + 1 :] = 1.0 / n_train
    
    p_lead = np.convolve(power_signal, lead_kernel, mode='same')
    p_lag = np.convolve(power_signal, lag_kernel, mode='same')
    
    noise_est = np.maximum(p_lead, p_lag)
    return alpha * noise_est

def compute_so_cfar(power_signal, n_guard, n_train, pfa):
    """Smallest-Of CFAR (Multi-Target Masking Specialist)"""
    N_half = n_train
    alpha = threshold_factor("SO", N_half, pfa)
    
    lead_kernel = np.zeros(2 * (n_train + n_guard) + 1)
    lead_kernel[:n_train] = 1.0 / n_train
    
    lag_kernel = np.zeros(2 * (n_train + n_guard) + 1)
    lag_kernel[n_train + 2 * n_guard + 1 :] = 1.0 / n_train
    
    p_lead = np.convolve(power_signal, lead_kernel, mode='same')
    p_lag = np.convolve(power_signal, lag_kernel, mode='same')
    
    noise_est = np.minimum(p_lead, p_lag)
    return alpha * noise_est

def compute_os_cfar(power_signal, n_guard, n_train, pfa, k_rank_ratio=0.75):
    """Ordered-Statistic CFAR"""
    N_ref = 2 * n_train
    k_idx = int(round(k_rank_ratio * N_ref)) - 1
    alpha = threshold_factor("OS", n_train, pfa, k_idx + 1)
    
    L = len(power_signal)
    threshold = np.zeros(L)
    half_w = n_train + n_guard
    
    # Fast sliding window sampling
    for i in range(half_w, L - half_w):
        ref_lead = power_signal[i - half_w : i - n_guard]
        ref_lag = power_signal[i + n_guard + 1 : i + half_w + 1]
        ref_pool = np.concatenate([ref_lead, ref_lag])
        sorted_ref = np.sort(ref_pool)
        threshold[i] = alpha * sorted_ref[k_idx]
        
    threshold[:half_w] = threshold[half_w]
    threshold[L - half_w:] = threshold[L - half_w - 1]
    return threshold

def run_upgrade2_cfar():
    print("=" * 80)
    print("RUNNING UPGRADE 2: ADVANCED CFAR FAMILY BENCHMARK (CA, GO, SO, OS)")
    print("=" * 80)
    
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "track1")
    os.makedirs(out_dir, exist_ok=True)
    
    # Grid parameters
    fs = 16.0e6
    c = 3.0e8
    dt = 1.0 / fs
    dr = c / (2.0 * fs)  # 9.375 m
    
    # Scenario: 400 range cells around 200 km
    N_cells = 500
    r_km = 200.0 + (np.arange(N_cells) - 250) * dr / 1e3
    
    # -------------------------------------------------------------
    # Scenario 1: Multi-Target Masking (Cluster Deployment)
    # -------------------------------------------------------------
    np.random.seed(42)
    # Background AWGN noise (exponential distributed in power)
    noise_power = np.random.exponential(scale=1.0, size=N_cells)
    
    # Target 1: Strong rocket body (RCS 5 m^2) at cell 220
    idx_t1 = 220
    # Target 2: Secondary satellite (8 dB weaker) at cell 232 (separated by 12 cells = 112.5 m)
    # This places Target 2 directly inside the reference training window of Target 1!
    idx_t2 = 232
    
    sig_multi = np.copy(noise_power)
    # Model compressed sinc responses
    for i in range(N_cells):
        s1 = np.sinc((i - idx_t1) * 0.25) ** 2
        s2 = np.sinc((i - idx_t2) * 0.25) ** 2
        sig_multi[i] += 400.0 * s1 + 65.0 * s2  # Strong target + weaker target
        
    n_guard = 4
    n_train = 16
    pfa = 1e-5
    
    thr_ca_m = compute_ca_cfar(sig_multi, n_guard, n_train, pfa)
    thr_so_m = compute_so_cfar(sig_multi, n_guard, n_train, pfa)
    thr_os_m = compute_os_cfar(sig_multi, n_guard, n_train, pfa, k_rank_ratio=0.75)
    
    # -------------------------------------------------------------
    # Scenario 2: Clutter Edge Transition (+15 dB clutter step)
    # -------------------------------------------------------------
    np.random.seed(101)
    sig_clutter = np.zeros(N_cells)
    # Left region: low thermal noise (scale 1.0)
    sig_clutter[:250] = np.random.exponential(scale=1.0, size=250)
    # Right region: dense clutter patch (+15 dB = 31.6x power)
    sig_clutter[250:] = np.random.exponential(scale=31.6, size=N_cells - 250)
    
    # Add a target right at the clutter boundary (cell 265)
    idx_tc = 265
    for i in range(N_cells):
        sc = np.sinc((i - idx_tc) * 0.25) ** 2
        sig_clutter[i] += 250.0 * sc
        
    thr_ca_c = compute_ca_cfar(sig_clutter, n_guard, n_train, pfa)
    thr_go_c = compute_go_cfar(sig_clutter, n_guard, n_train, pfa)
    thr_os_c = compute_os_cfar(sig_clutter, n_guard, n_train, pfa, k_rank_ratio=0.75)
    
    # -------------------------------------------------------------
    # Plotting Comparative Benchmark
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), facecolor='#080d1a')
    plt.suptitle("Advanced CFAR Detection Benchmark in Non-Homogeneous Environments\n"
                 "CA-CFAR vs. SO-CFAR (Multi-Target Masking) vs. GO-CFAR (Clutter Boundary) | Pfa = 10^-5",
                 color='#f8fafc', fontsize=13, fontweight='bold', y=0.98)
    
    for ax in (ax1, ax2):
        ax.set_facecolor('#0b1329')
        ax.grid(True, linestyle='--', alpha=0.35, color='#64748b')
        ax.tick_params(colors='#cbd5e1', labelsize=9)
        for spine in ax.spines.values():
            spine.set_color('#334155')
            
    # Panel 1: Multi-Target Masking
    ax1.plot(r_km, 10*np.log10(sig_multi + 1e-12), color='#38bdf8', lw=1.5, alpha=0.9, label="Radar Signal (Target 1 & 2)")
    ax1.plot(r_km, 10*np.log10(thr_ca_m + 1e-12), color='#f43f5e', lw=1.6, linestyle='--', label="CA-CFAR Threshold (Masks Target 2!)")
    ax1.plot(r_km, 10*np.log10(thr_so_m + 1e-12), color='#10b981', lw=1.8, label="SO-CFAR Threshold (Unmasks Target 2!)")
    ax1.plot(r_km, 10*np.log10(thr_os_m + 1e-12), color='#c084fc', lw=1.5, linestyle=':', label="OS-CFAR Threshold (Robust)")
    
    ax1.axvline(r_km[idx_t1], color='#38bdf8', linestyle=':', lw=1.2, label=f"Target 1 (R1 = {r_km[idx_t1]:.3f} km)")
    ax1.axvline(r_km[idx_t2], color='#fbbf24', linestyle=':', lw=1.2, label=f"Target 2 (R2 = {r_km[idx_t2]:.3f} km)")
    
    ax1.set_xlabel("Radar Range (km)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax1.set_ylabel("Power (dB)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax1.set_title("Scenario A: Multi-Target Masking (Close Spacecraft Separation at 200 km)\n"
                  "CA-CFAR threshold is inflated by Target 1, burying Target 2. SO-CFAR drops threshold, detecting BOTH targets!",
                  color='#f8fafc', fontsize=10, fontweight='bold')
    ax1.set_xlim(r_km[170], r_km[290])
    ax1.set_ylim(-5, 30)
    ax1.legend(loc='upper right', facecolor='#0f172a', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    
    # Panel 2: Clutter Edge Transition
    ax2.plot(r_km, 10*np.log10(sig_clutter + 1e-12), color='#38bdf8', lw=1.2, alpha=0.85, label="Radar Signal + Sea/Ground Clutter (+15 dB step)")
    ax2.plot(r_km, 10*np.log10(thr_ca_c + 1e-12), color='#f43f5e', lw=1.6, linestyle='--', label="CA-CFAR Threshold (Causes False Alarm Spikes at Edge)")
    ax2.plot(r_km, 10*np.log10(thr_go_c + 1e-12), color='#10b981', lw=1.8, label="GO-CFAR Threshold (Strict False Alarm Regulation)")
    ax2.plot(r_km, 10*np.log10(thr_os_c + 1e-12), color='#c084fc', lw=1.5, linestyle=':', label="OS-CFAR Threshold")
    
    ax2.axvline(r_km[250], color='#fbbf24', linestyle='--', lw=1.5, label="Clutter Boundary (Step at 200.0 km)")
    ax2.axvline(r_km[idx_tc], color='#10b981', linestyle=':', lw=1.2, label="Embedded Target in Clutter")
    
    ax2.set_xlabel("Radar Range (km)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax2.set_ylabel("Power (dB)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax2.set_title("Scenario B: Clutter Boundary Transition (+15 dB Clutter Edge)\n"
                  "CA-CFAR underestimates noise at edge -> massive false alarms. GO-CFAR selects maximum, using the calibrated GO threshold (clutter-edge Pfa must be measured)",
                  color='#f8fafc', fontsize=10, fontweight='bold')
    ax2.set_xlim(r_km[180], r_km[320])
    ax2.set_ylim(-5, 35)
    ax2.legend(loc='upper left', facecolor='#0f172a', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    
    plt.tight_layout()
    out_path = os.path.join(out_dir, "fig10_cfar_family_comparison.png")
    artifact_io.save_figure(plt.gcf(), out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[Generated] {out_path}")
    print("Upgrade 2 CFAR Family comparison completed successfully!")

if __name__ == "__main__":
    run_upgrade2_cfar()
