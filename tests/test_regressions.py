"""Regression checks for the numerical and reporting failures found in review."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

import advanced_upgrade2_cfar_family as cfar
import advanced_upgrade3_coherent_range_doppler as cpi
import advanced_upgrade4_nlfm_waveform as nlfm
import advanced_upgrade5_hardware_imperfections as hardware
import track1_lfm_simulation as core
import track1_bonus_upgrades as bonus
import json
import os


class NumericalRegressions(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows file-sharing regression")
    def test_regeneration_with_transient_windows_preview_lock(self):
        import ctypes
        import threading
        import artifact_io
        from ctypes import wintypes
        from PIL import Image
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "fig1_prt_pulse_train.png"
            figure = plt.figure()
            figure.savefig(target)
            plt.close(figure)
            # Allow readers and replacement, but deny in-place truncation/writes.
            handle = kernel.CreateFileW(str(target), 0x80000000, 1 | 4, None, 3, 0x80, None)
            self.assertNotEqual(handle, ctypes.c_void_p(-1).value)
            release = threading.Timer(0.6, kernel.CloseHandle, args=(handle,))
            release.start()
            try:
                replacement = plt.figure()
                replacement.add_subplot().plot([0, 1], [1, 0])
                artifact_io.save_figure(replacement, target)
            finally:
                release.join()
                plt.close("all")
            with Image.open(target) as image:
                image.verify()

    def test_high_velocity_doppler_peak_search_contains_target(self):
        with tempfile.TemporaryDirectory() as directory, patch("artifact_io.save_figure"), contextlib.redirect_stdout(io.StringIO()):
            estimates = bonus.run_doppler_coupling_experiment(directory, vr_true=7500.0)
        plt.close("all")
        self.assertLess(abs(estimates["range_error_m"]), core.SAMPLE_SPACING)
        self.assertLess(abs(estimates["velocity_ms"] - 7500), 65)

    def test_streamlit_default_and_out_of_range_inputs(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=60)
        self.assertEqual(list(app.exception), [])
        target = next(item for item in app.number_input if item.label == "Target Range (km)")
        target.set_value(350.0).run(timeout=60)
        self.assertEqual(list(app.exception), [])
        self.assertTrue(any("valid receive window" in item.value for item in app.error))

    def test_core_exports_reproducible_results(self):
        with tempfile.TemporaryDirectory() as directory, patch("artifact_io.save_figure"), contextlib.redirect_stdout(io.StringIO()):
            result = core.run_simulation(output_dir=directory)
            saved = json.loads((Path(directory) / "simulation_results.json").read_text())
        plt.close("all")
        self.assertEqual(saved["cfar_margin_2"], result["cfar_margin_2"])
        self.assertAlmostEqual(saved["cfar_margin_2"], 10.07566, places=3)
        self.assertTrue(saved["monte_carlo"]["mean_ci95_db"][0] < 10 < saved["monte_carlo"]["mean_ci95_db"][1])

    def test_cfar_family_noise_only_false_alarm_probability(self):
        noise = np.random.default_rng(731).exponential(size=200_000)
        for name in ("compute_ca_cfar", "compute_go_cfar", "compute_so_cfar", "compute_os_cfar"):
            with self.subTest(detector=name):
                threshold = getattr(cfar, name)(noise, 4, 16, 1e-3)
                measured = np.mean(noise[100:-100] > threshold[100:-100])
                self.assertAlmostEqual(measured, 1e-3, delta=0.0003)

    def test_cpi_uses_unaliased_fft_bins_and_window_gain(self):
        with patch("artifact_io.save_figure"), contextlib.redirect_stdout(io.StringIO()):
            result = cpi.run_upgrade3_coherent_cpi()
        plt.close("all")
        self.assertIsInstance(result, dict)
        self.assertAlmostEqual(result["measured_doppler_hz"], result["target_doppler_hz"])
        self.assertAlmostEqual(result["window_gain_db"], 13.1527043478, places=6)

    def test_nlfm_reports_measured_sidelobes(self):
        with patch("artifact_io.save_figure"), contextlib.redirect_stdout(io.StringIO()):
            result = nlfm.run_upgrade4_nlfm()
        plt.close("all")
        self.assertIsInstance(result, dict)
        self.assertAlmostEqual(result["nlfm_psl_db"], -29.30444, places=3)
        self.assertAlmostEqual(result["nlfm_mismatch_db"], 0, places=8)

    def test_hardware_phase_rms_matches_labels(self):
        with patch("artifact_io.save_figure"), contextlib.redirect_stdout(io.StringIO()):
            result = hardware.run_upgrade5_hardware()
        plt.close("all")
        for requested, measured in result["phase_rms_degrees"].items():
            self.assertAlmostEqual(requested, measured, places=8)

    def test_submission_contains_tests_and_current_core(self):
        import zipfile
        from pypdf import PdfReader
        root = Path(__file__).resolve().parents[1]
        results = json.loads((root / "figures/track1/simulation_results.json").read_text())
        for name, pages in (("TECHNICAL_NOTE_IEEE.pdf", 2), ("PITCH_DECK.pdf", 5)):
            pdf = PdfReader(root / name)
            self.assertEqual(len(pdf.pages), pages)
            text = " ".join(page.extract_text() for page in pdf.pages)
            self.assertIn(f"{results['cfar_margin_1']:.2f} dB", text)
            self.assertIn(f"{results['cfar_margin_2']:.2f} dB", text)
            self.assertNotIn("{{", text)
        with zipfile.ZipFile(root / "submission_bundle.zip") as bundle:
            self.assertIsNone(bundle.testzip())
            self.assertIn("tests/test_regressions.py", bundle.namelist())
            for name in ("track1_lfm_simulation.py", "radar_metrics.py", "requirements.txt"):
                self.assertEqual(bundle.read(name), (root / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
