"""
Comprehensive Radar Simulation Stress & Verification Test Suite
==============================================================
Beyond the Signal: Radar Systems & Applied Space-Tech Research-Athon (Utkrishta 2026)
Track 1: Radar Signal Processing (Curated by Mr. Rajendra Kumar, Scientist, SDSC SHAR, ISRO)

Executes rigorous stress testing across four operational domains:
  1. Deliverables Integrity & Format Compliance:
     - Technical Note strictly 2 pages (IEEE standard)
     - Pitch Deck strictly 5 slides (PDF & PPTX)
     - Submission ZIP archive CRC32 integrity check
     - All 13 Figures validated (PNG headers, non-empty)
     - Google Colab notebook JSON schema validation
  2. Script Execution & Reproducibility Verification:
     - Executes core, bonus, advanced and document generation scripts with zero exit codes.
  3. Monte Carlo & Statistical SNR Consistency:
     - 200-trial Monte Carlo verification of the +10.0 dB SNR enhancement.
     - Confirms 95% confidence interval and standard deviation.
  4. Numerical Boundary & Extreme Dynamics Stress Tests:
     - Fractional delay straddling loss sweep (sub-bin sampling offsets)
     - Extreme orbital velocity (v_r = 7500 m/s, Mach 22, Doppler = 150 kHz)
     - Micro-RCS deep-space tracking (sigma = 0.005 m^2 at R = 350 km)
     - Finite-output check on the production matched filter.
"""

import os
import sys
import json
import zipfile
import subprocess
import numpy as np
import scipy.signal as signal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
import track1_lfm_simulation as radar

class RadarStressTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []
        
    def log_result(self, category, name, passed, details=""):
        status_str = "PASS" if passed else "FAIL"
        if passed:
            self.passed += 1
            print(f"  [PASS] {name:<50} {details}")
        else:
            self.failed += 1
            print(f"  [FAIL] {name:<50} {details}")
        self.results.append({"category": category, "test": name, "status": status_str, "details": details})

    # =========================================================================
    # SUITE 1: Deliverable Integrity & Format Compliance
    # =========================================================================
    def test_deliverables_integrity(self):
        print("\n" + "=" * 80)
        print("SUITE 1: DELIVERABLE INTEGRITY & FORMAT COMPLIANCE TESTS")
        print("=" * 80)
        
        # 1. Technical Note PDF Page Count
        pdf_path = os.path.join(BASE_DIR, "TECHNICAL_NOTE_IEEE.pdf")
        if os.path.exists(pdf_path):
            try:
                import pypdf
                reader = pypdf.PdfReader(pdf_path)
                page_count = len(reader.pages)
                self.log_result("Deliverables", "IEEE Technical Note PDF Page Count", page_count == 2, f"Pages: {page_count} (Required: Exactly 2)")
            except Exception as e:
                self.log_result("Deliverables", "IEEE Technical Note PDF Read", False, str(e))
        else:
            self.log_result("Deliverables", "IEEE Technical Note PDF Exists", False, "File missing")

        # 2. Pitch Deck PDF Slide Count
        deck_pdf_path = os.path.join(BASE_DIR, "PITCH_DECK.pdf")
        if os.path.exists(deck_pdf_path):
            try:
                import pypdf
                reader = pypdf.PdfReader(deck_pdf_path)
                slide_count = len(reader.pages)
                self.log_result("Deliverables", "Pitch Deck PDF Slide Count", slide_count == 5, f"Slides: {slide_count} (Required: Exactly 5)")
            except Exception as e:
                self.log_result("Deliverables", "Pitch Deck PDF Read", False, str(e))
        else:
            self.log_result("Deliverables", "Pitch Deck PDF Exists", False, "File missing")

        # 3. Pitch Deck PPTX Slide Count
        pptx_path = os.path.join(BASE_DIR, "PITCH_DECK.pptx")
        if os.path.exists(pptx_path):
            try:
                from pptx import Presentation
                prs = Presentation(pptx_path)
                slide_count = len(prs.slides)
                self.log_result("Deliverables", "Pitch Deck PPTX Slide Count", slide_count == 5, f"Slides: {slide_count} (Required: Exactly 5)")
            except Exception as e:
                self.log_result("Deliverables", "Pitch Deck PPTX Read", False, str(e))
        else:
            self.log_result("Deliverables", "Pitch Deck PPTX Exists", False, "File missing")

        # 4. Submission ZIP Archive CRC Integrity Check
        zip_path = os.path.join(BASE_DIR, "submission_bundle.zip")
        if os.path.exists(zip_path):
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    bad_file = zf.testzip()
                    file_count = len(zf.namelist())
                    is_valid = (bad_file is None) and (file_count >= 30)
                    self.log_result("Deliverables", "Submission ZIP CRC32 Integrity", is_valid, f"{file_count} files verified clean, CRC OK")
            except Exception as e:
                self.log_result("Deliverables", "Submission ZIP Read", False, str(e))
        else:
            self.log_result("Deliverables", "Submission ZIP Exists", False, "File missing")

        # 5. Publication Figures Verification (All 13 PNGs)
        figures_dir = os.path.join(BASE_DIR, "figures", "track1")
        if os.path.exists(figures_dir):
            figs = [f for f in os.listdir(figures_dir) if f.endswith(".png")]
            all_valid_size = all(os.path.getsize(os.path.join(figures_dir, f)) > 50000 for f in figs)
            self.log_result("Deliverables", "All 13 Publication Figures Exist & Valid", len(figs) == 13 and all_valid_size, f"Found {len(figs)}/13 valid PNGs (>50 KB)")
        else:
            self.log_result("Deliverables", "Figures Directory Exists", False, "Missing figures/track1")

        # 6. Colab Notebook JSON Schema Validation
        nb_path = os.path.join(BASE_DIR, "track1_radar_notebook.ipynb")
        if os.path.exists(nb_path):
            try:
                with open(nb_path, "r", encoding="utf-8") as f:
                    nb_data = json.load(f)
                cells = nb_data.get("cells", [])
                code_cells = [c for c in cells if c.get("cell_type") == "code"]
                has_code = len(code_cells) >= 6
                self.log_result("Deliverables", "Jupyter / Colab Notebook Schema", has_code, f"{len(cells)} cells ({len(code_cells)} executable code blocks)")
            except Exception as e:
                self.log_result("Deliverables", "Notebook JSON Parse", False, str(e))
        else:
            self.log_result("Deliverables", "Notebook Exists", False, "File missing")

    # =========================================================================
    # SUITE 2: Script Execution & Reproducibility Verification
    # =========================================================================
    def test_script_execution(self):
        print("\n" + "=" * 80)
        print("SUITE 2: SCRIPT EXECUTION & REPRODUCIBILITY VERIFICATION")
        print("=" * 80)
        
        scripts = [
            "track1_lfm_simulation.py",
            "track1_bonus_upgrades.py",
            "advanced_upgrade1_ambiguity.py",
            "advanced_upgrade2_cfar_family.py",
            "advanced_upgrade3_coherent_range_doppler.py",
            "advanced_upgrade4_nlfm_waveform.py",
            "advanced_upgrade5_hardware_imperfections.py",
            "scripts/generate_pdf_report.py",
            "scripts/generate_pitch_deck.py",
            "scripts/generate_pitch_deck_pdf.py",
        ]
        
        for script in scripts:
            script_path = os.path.join(BASE_DIR, script)
            if not os.path.exists(script_path):
                self.log_result("Execution", f"File Exists: {script}", False, "File missing")
                continue
            
            try:
                res = subprocess.run([sys.executable, script_path],
                                     cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", timeout=60,
                                     env={**os.environ, "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg"})
                passed = (res.returncode == 0) and ("Traceback" not in res.stderr)
                err_msg = res.stderr.strip()[-2000:] if not passed else "Execution clean (code 0)"
                self.log_result("Execution", f"Execute: {script}", passed, err_msg)
            except subprocess.TimeoutExpired:
                self.log_result("Execution", f"Execute: {script}", False, "Timeout after 60s")
            except Exception as e:
                self.log_result("Execution", f"Execute: {script}", False, str(e))

    # =========================================================================
    # SUITE 3: Monte Carlo & Statistical SNR Consistency
    # =========================================================================
    def test_monte_carlo_snr_consistency(self, n_trials=200):
        print("\n" + "=" * 80)
        print(f"SUITE 3: MONTE CARLO STATISTICAL SNR CONSISTENCY ({n_trials} TRIALS)")
        print("=" * 80)
        
        result = radar.monte_carlo_snr(n_trials)
        mean, std = result["mean_boost_db"], result["std_boost_db"]
        lo, hi = result["mean_ci95_db"]
        self.log_result("Monte Carlo", f"Production SNR Boost over {n_trials} Trials",
                        lo <= 10 <= hi and abs(mean - 10) < 0.35,
                        f"Mean: {mean:.2f} dB; Std: {std:.2f} dB; 95% CI for mean: [{lo:.2f}, {hi:.2f}]")

    # =========================================================================
    # SUITE 4: Numerical Boundary & Extreme Dynamics Stress Tests
    # =========================================================================
    def test_numerical_and_boundary_stress(self):
        print("\n" + "=" * 80)
        print("SUITE 4: NUMERICAL BOUNDARY & EXTREME DYNAMICS STRESS TESTS")
        print("=" * 80)
        
        c = 3.0e8
        B = 4.0e6
        tau_p = 100.0e-6
        fs = 16.0e6
        dt = 1.0 / fs
        
        # 1. Fractional Delay Straddling Loss Sweep
        straddling_losses = []
        kr = B / tau_p
        n_p = int(round(tau_p * fs))
        t_p = np.arange(n_p) * dt - tau_p / 2.0
        ref_pulse = np.exp(1j * np.pi * kr * (t_p ** 2))
        h_matched = np.conj(ref_pulse[::-1])
        
        for frac_offset in np.linspace(0.0, 1.0, 21):
            # Shift pulse by fractional sample offset using sinc interpolation
            t_shifted = t_p - frac_offset * dt
            shifted_pulse = np.exp(1j * np.pi * kr * (t_shifted ** 2))
            compressed = signal.fftconvolve(shifted_pulse, h_matched, mode='same')
            peak_power = np.max(np.abs(compressed) ** 2)
            straddling_losses.append(peak_power)
            
        max_straddling_loss_db = 10.0 * np.log10(np.min(straddling_losses) / np.max(straddling_losses))
        straddle_pass = abs(max_straddling_loss_db) <= 1.2  # Theoretical sinc straddling loss <= 0.9 dB
        self.log_result("Boundary Stress", "Fractional Delay Straddling Loss", straddle_pass,
                        f"Worst-case straddling drop: {max_straddling_loss_db:.2f} dB (Tolerance: <= 1.2 dB)")

        # Exercise the production waveform echo and matched-filter estimator.
        from tempfile import TemporaryDirectory
        from track1_bonus_upgrades import run_doppler_coupling_experiment
        with TemporaryDirectory() as output:
            estimates = run_doppler_coupling_experiment(output_dir=output, vr_true=7500.0)
        dyn_pass = abs(estimates["range_error_m"]) < radar.SAMPLE_SPACING and abs(estimates["velocity_ms"] - 7500) < 65
        self.log_result("Boundary Stress", "7500 m/s waveform Doppler decoupling", dyn_pass,
                        f"Range error: {estimates['range_error_m']:.2f} m; velocity: {estimates['velocity_ms']:.1f} m/s")
        lambda_c = c / 3e9

        # 3. Micro-RCS Deep Space Tracking (sigma = 0.005 m^2 at 350 km)
        Pt = 250.0e3
        G = 10.0 ** (40.0 / 10.0)
        R_deep = 350.0e3
        rcs_micro = 0.005
        L = 10.0 ** (3.0 / 10.0)
        Pr_micro = (Pt * (G**2) * (lambda_c**2) * rcs_micro) / (((4.0 * np.pi)**3) * (R_deep**4) * L)
        
        N0 = 1.380649e-23 * 290.0 * (10.0 ** (2.5 / 10.0))
        Er_micro = Pr_micro * tau_p
        snr_micro_db = 10.0 * np.log10(Er_micro / N0)
        # With coherent integration M=32 pulses:
        snr_micro_cpi_db = snr_micro_db + 10.0 * np.log10(32)
        
        # This ideal integration estimate is below our single-cell detection requirement.
        deep_pass = np.isfinite(snr_micro_cpi_db) and snr_micro_cpi_db < 13.18
        self.log_result("Boundary Stress", "Micro-RCS Deep Space Tracking (350 km, 0.005 m^2)", deep_pass,
                        f"Single Pulse SNR: {snr_micro_db:.2f} dB | Ideal M=32 CPI: {snr_micro_cpi_db:.2f} dB (below 13.18 dB requirement; 350 km exceeds the 300 km PRI range)")

        # 4. Zero NaN / Inf Sanity Check Across Large Dynamic Ranges
        test_inputs = [
            np.zeros(1000, dtype=complex),
            np.ones(1000, dtype=complex) * 1e-15,
            np.ones(1000, dtype=complex) * 1e12,
            np.random.randn(1000) + 1j * np.random.randn(1000)
        ]
        has_nans = False
        for inp in test_inputs:
            h = np.ones(100, dtype=complex)
            out = radar.matched_filter(inp, h)
            if np.any(np.isnan(out)) or np.any(np.isinf(out)):
                has_nans = True
                break
        self.log_result("Boundary Stress", "Production filter finite-output check", not has_nans,
                        "Robust from 1e-15 to 1e12 amplitude spans")

    # =========================================================================
    # Summary & Scorecard
    # =========================================================================
    def print_summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 80)
        print("RADAR SIMULATION STRESS TEST AUDIT SCORECARD")
        print("=" * 80)
        print(f"  TOTAL TESTS RUN   : {total}")
        print(f"  PASSED            : {self.passed}")
        print(f"  FAILED            : {self.failed}")
        print(f"  OVERALL STATUS    : {'[SUCCESS - 100% PASS]' if self.failed == 0 else '[FAILED CHECKS DETECTED]'}")
        print("=" * 80)
        return self.failed == 0

def run_stress_test_suite():
    suite = RadarStressTestSuite()
    suite.test_deliverables_integrity()
    suite.test_script_execution()
    suite.test_monte_carlo_snr_consistency(n_trials=200)
    suite.test_numerical_and_boundary_stress()
    import unittest
    regressions = unittest.defaultTestLoader.discover(os.path.join(BASE_DIR, "tests"), pattern="test_regressions.py")
    result = unittest.TextTestRunner(verbosity=2).run(regressions)
    suite.log_result("Regression", "Numerical regression suite", result.wasSuccessful())
    success = suite.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(run_stress_test_suite())
