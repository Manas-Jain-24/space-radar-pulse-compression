"""
Advanced Radar Upgrade 1: Woodward Ambiguity Function & 3D Delay-Doppler Surface
================================================================================
Beyond the Signal: Radar Systems & Applied Space-Tech Research-Athon (Utkrishta 2026)
Track 1: Radar Signal Processing (Curated by Mr. Rajendra Kumar, Scientist, SDSC SHAR, ISRO)

Theoretical Background:
-----------------------
The Woodward Ambiguity Function chi(tau, nu) characterizes the matched filter output
when a target echo is delayed by tau and Doppler-shifted by nu:
    chi(tau, nu) = integral_{-inf}^{inf} s(t) s*(t - tau) exp(j * 2 * pi * nu * t) dt

Analytical properties (the plots do not numerically validate the volume integral):
  1. Peak Value: |chi(0, 0)|^2 = 1 (Normalized total energy)
  2. Volume Invariance: iintegral |chi(tau, nu)|^2 dtau dnu = 1 (Energy conservation)
  3. LFM Ridge Shearing: For chirp slope kr = B / tau_p, the ambiguity ridge lies along
     nu + kr * tau = 0  ==>  Delta tau = -nu / kr.
     This proves LFM's inherent Doppler tolerance: a Doppler-shifted echo still compresses
     cleanly with minimal peak power loss, producing only a predictable time shift.
  4. Comparison: Unmodulated rectangular pulse vs 10 us LFM chirp vs 100 us LFM chirp.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import artifact_io
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

def compute_lfm_ambiguity_analytical(tau_grid, nu_grid, tau_p, B):
    """
    Computes the exact closed-form Woodward Ambiguity magnitude for an LFM pulse:
      |chi(tau, nu)| = |(1 - |tau|/tau_p) * sinc((nu + kr*tau) * (tau_p - |tau|))|
    for |tau| <= tau_p, and 0 elsewhere.
    """
    kr = B / tau_p
    T, N = np.meshgrid(tau_grid, nu_grid)
    
    chi = np.zeros_like(T, dtype=float)
    valid_mask = np.abs(T) <= tau_p
    
    T_val = T[valid_mask]
    N_val = N[valid_mask]
    
    # Triangle window envelope
    env = 1.0 - np.abs(T_val) / tau_p
    
    # Sinc argument: pi * (nu + kr*tau) * (tau_p - |tau|)
    arg = np.pi * (N_val + kr * T_val) * (tau_p - np.abs(T_val))
    
    # Safe sinc calculation: sin(x)/x
    sinc_val = np.ones_like(arg)
    nonzero = np.abs(arg) > 1e-12
    sinc_val[nonzero] = np.sin(arg[nonzero]) / arg[nonzero]
    
    chi[valid_mask] = env * np.abs(sinc_val)
    return chi

def compute_unmodulated_ambiguity(tau_grid, nu_grid, tau_p):
    """
    Computes analytical ambiguity magnitude for unmodulated pulse (kr = 0):
      |chi(tau, nu)| = |(1 - |tau|/tau_p) * sinc(nu * (tau_p - |tau|))|
    """
    return compute_lfm_ambiguity_analytical(tau_grid, nu_grid, tau_p, B=0.0)

def run_upgrade1_ambiguity():
    print("=" * 80)
    print("RUNNING UPGRADE 1: WOODWARD AMBIGUITY FUNCTION & DELAY-DOPPLER SURFACE")
    print("=" * 80)
    
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "track1")
    os.makedirs(out_dir, exist_ok=True)
    
    c = 3.0e8
    B = 4.0e6           # 4 MHz bandwidth
    tau1 = 10.0e-6      # 10 us pulse
    tau2 = 100.0e-6     # 100 us pulse
    
    # Grid for detailed visualization:
    # Delay grid: normalized to range delta_R = c / (2B) = 37.5 m
    delta_tau = 1.0 / B
    tau_span = 3.0 * tau1
    tau_axis = np.linspace(-tau_span, tau_span, 301)
    
    # Doppler grid: span +/- 200 kHz (covers Mach 5 velocity 30 kHz easily)
    nu_span = 150.0e3
    nu_axis = np.linspace(-nu_span, nu_span, 301)
    
    print(f"Computing Ambiguity Surfaces...")
    print(f"  Pulse 1: tau_p = {tau1*1e6:.1f} us, Bandwidth = {B/1e6:.1f} MHz, Slope kr = {B/tau1:.2e} Hz/s")
    print(f"  Pulse 2: tau_p = {tau2*1e6:.1f} us, Bandwidth = {B/1e6:.1f} MHz, Slope kr = {B/tau2:.2e} Hz/s")
    
    chi_lfm1 = compute_lfm_ambiguity_analytical(tau_axis, nu_axis, tau1, B)
    chi_unmod = compute_unmodulated_ambiguity(tau_axis, nu_axis, tau1)
    
    # Delay axis in range equivalent: R = c * tau / 2
    range_axis_m = (c * tau_axis / 2.0)
    nu_axis_khz = nu_axis / 1e3
    
    # Convert to dB for contours (clip at -30 dB)
    chi_lfm1_db = 20.0 * np.log10(chi_lfm1 + 1e-12)
    chi_lfm1_db = np.clip(chi_lfm1_db, -30.0, 0.0)
    
    chi_unmod_db = 20.0 * np.log10(chi_unmod + 1e-12)
    chi_unmod_db = np.clip(chi_unmod_db, -30.0, 0.0)
    
    # -------------------------------------------------------------
    # Multi-Panel Figure: 3D Surface, 2D Contours, and 1D Cuts
    # -------------------------------------------------------------
    fig = plt.figure(figsize=(16, 11), facecolor='#080d1a')
    plt.suptitle("Woodward Ambiguity Function: LFM Pulse Compression & Doppler Tolerance\n"
                 "SDSC SHAR S-band Tracking Radar (B = 4.0 MHz, tau = 10 us & 100 us)",
                 color='#f8fafc', fontsize=14, fontweight='bold', y=0.98)
    
    # Panel 1: 3D Surface of LFM Ambiguity Function
    ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#0b1329')
    R_mesh, N_mesh = np.meshgrid(range_axis_m, nu_axis_khz)
    surf = ax1.plot_surface(R_mesh, N_mesh, chi_lfm1, cmap=cm.viridis,
                            linewidth=0, antialiased=True, alpha=0.92)
    ax1.set_xlabel("\nRange Offset (m)", color='#cbd5e1', fontsize=9, fontweight='bold')
    ax1.set_ylabel("\nDoppler Shift (kHz)", color='#cbd5e1', fontsize=9, fontweight='bold')
    ax1.set_zlabel("\n|chi(tau, nu)|", color='#cbd5e1', fontsize=9, fontweight='bold')
    ax1.set_title("3D Ambiguity Surface |chi(tau, nu)| (LFM Chirp, tau=10 us, B=4 MHz)\n"
                  "Clear Sheared Diagonal Ridge Demonstrating Doppler Tolerance",
                  color='#f8fafc', fontsize=10, fontweight='bold')
    ax1.tick_params(colors='#cbd5e1', labelsize=8)
    ax1.view_init(elev=32, azim=-55)
    
    # Panel 2: 2D Contour Comparison - Unmodulated vs LFM
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#0b1329')
    levels = np.linspace(-30, 0, 13)
    cs = ax2.contourf(range_axis_m, nu_axis_khz, chi_lfm1_db, levels=levels, cmap=cm.plasma)
    cbar = fig.colorbar(cs, ax=ax2, orientation='vertical', pad=0.03)
    cbar.set_label("Matched Filter Response (dB)", color='#cbd5e1', fontsize=9, fontweight='bold')
    cbar.ax.tick_params(colors='#cbd5e1', labelsize=8)
    
    # Overplot the theoretical ridge line: Delta tau = -nu / kr ==> Delta R = -c * nu / (2 * kr)
    kr1 = B / tau1
    ridge_nu_khz = np.linspace(-100, 100, 100)
    ridge_range_m = -c * (ridge_nu_khz * 1e3) / (2.0 * kr1)
    ax2.plot(ridge_range_m, ridge_nu_khz, 'w--', lw=1.8, label="Ambiguity Ridge: nu + kr*tau = 0")
    
    # Mark Mach 5 Doppler point (30 kHz)
    mach5_nu = 30.0  # kHz
    mach5_r = -c * (mach5_nu * 1e3) / (2.0 * kr1)
    ax2.plot(mach5_r, mach5_nu, 'ro', markersize=7, label=f"Mach 5 Doppler (+30 kHz, {mach5_r:.1f} m)")
    
    ax2.set_xlabel("Range Offset (meters)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax2.set_ylabel("Doppler Shift (kHz)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax2.set_title("2D Ambiguity Contour (dB) & Sheared Ridge Line\n"
                  "Shows Range-Doppler Coupling Trajectory (Slope = -c / 2kr)",
                  color='#f8fafc', fontsize=10, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.3, color='#64748b')
    ax2.tick_params(colors='#cbd5e1', labelsize=8)
    ax2.set_xlim(-1500, 1500)
    ax2.set_ylim(-150, 150)
    ax2.legend(loc='lower left', facecolor='#0f172a', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    for spine in ax2.spines.values():
        spine.set_color('#334155')
        
    # Panel 3: Zero-Doppler Cut (Range Resolution Function |chi(tau, 0)|)
    ax3 = fig.add_subplot(2, 2, 3, facecolor='#0b1329')
    zero_dop_idx = len(nu_axis) // 2
    cut_range_unmod = chi_unmod[zero_dop_idx, :]
    cut_range_lfm = chi_lfm1[zero_dop_idx, :]
    
    # Zoom around center +/- 150 meters
    zoom_m = 150.0
    mask_zoom = (range_axis_m >= -zoom_m) & (range_axis_m <= zoom_m)
    r_zoom = range_axis_m[mask_zoom]
    
    ax3.plot(r_zoom, 20*np.log10(cut_range_unmod[mask_zoom] + 1e-12),
             color='#94a3b8', lw=1.5, linestyle=':', label="Unmodulated Pulse (Width = 1500 m)")
    ax3.plot(r_zoom, 20*np.log10(cut_range_lfm[mask_zoom] + 1e-12),
             color='#38bdf8', lw=2.0, label="LFM Chirp (Rayleigh Width = 37.5 m)")
    ax3.axhline(-3.0, color='#fbbf24', linestyle='--', lw=1.2, label="-3 dB Resolution Line")
    ax3.axvline(37.5/2.0, color='#10b981', linestyle=':', lw=1.0)
    ax3.axvline(-37.5/2.0, color='#10b981', linestyle=':', lw=1.0)
    
    ax3.set_xlabel("Range Relative to Target (meters)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax3.set_ylabel("Normalized Response (dB)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax3.set_title("Zero-Doppler Cut |chi(tau, 0)|: Range Resolution Proof\n"
                  "LFM Compresses Range by 40x Compared to Unmodulated Pulse",
                  color='#f8fafc', fontsize=10, fontweight='bold')
    ax3.set_ylim(-35, 2)
    ax3.set_xlim(-zoom_m, zoom_m)
    ax3.grid(True, linestyle='--', alpha=0.3, color='#64748b')
    ax3.tick_params(colors='#cbd5e1', labelsize=8)
    ax3.legend(loc='upper right', facecolor='#0f172a', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    for spine in ax3.spines.values():
        spine.set_color('#334155')

    # Panel 4: Zero-Delay Cut (Doppler Response |chi(0, nu)|)
    ax4 = fig.add_subplot(2, 2, 4, facecolor='#0b1329')
    zero_tau_idx = len(tau_axis) // 2
    cut_dop_10 = chi_lfm1[:, zero_tau_idx]
    
    # Compute for 100 us pulse on the same nu_axis
    chi_lfm2_cut = compute_lfm_ambiguity_analytical(np.array([0.0]), nu_axis, tau2, B)[:, 0]
    
    ax4.plot(nu_axis_khz, 20*np.log10(cut_dop_10 + 1e-12),
             color='#38bdf8', lw=1.8, label=f"tau1 = 10 us (Doppler Nulls at +/-100 kHz)")
    ax4.plot(nu_axis_khz, 20*np.log10(chi_lfm2_cut + 1e-12),
             color='#ec4899', lw=1.8, label=f"tau2 = 100 us (Doppler Nulls at +/-10 kHz)")
    ax4.axhline(-3.0, color='#fbbf24', linestyle='--', lw=1.2, label="-3 dB Doppler Width")
    
    ax4.set_xlabel("Doppler Frequency Shift (kHz)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax4.set_ylabel("Normalized Response (dB)", color='#cbd5e1', fontsize=10, fontweight='bold')
    ax4.set_title("Zero-Delay Cut |chi(0, nu)|: Doppler Selectivity\n"
                  "100 us Pulse Exhibits 10x Narrower Doppler Mainlobe (Higher Velocity Sensitivity)",
                  color='#f8fafc', fontsize=10, fontweight='bold')
    ax4.set_ylim(-35, 2)
    ax4.set_xlim(-150, 150)
    ax4.grid(True, linestyle='--', alpha=0.3, color='#64748b')
    ax4.tick_params(colors='#cbd5e1', labelsize=8)
    ax4.legend(loc='upper right', facecolor='#0f172a', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    for spine in ax4.spines.values():
        spine.set_color('#334155')
        
    plt.tight_layout()
    out_path = os.path.join(out_dir, "fig9_ambiguity_function_3d_and_contours.png")
    artifact_io.save_figure(plt.gcf(), out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[Generated] {out_path}")
    print("Upgrade 1 Ambiguity Function analysis completed successfully!")

if __name__ == "__main__":
    run_upgrade1_ambiguity()
