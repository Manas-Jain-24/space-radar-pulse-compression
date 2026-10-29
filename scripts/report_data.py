"""One source of computed baseline metrics for submission documents."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from artifact_io import atomic_output


def load_results():
    path = ROOT / "figures/track1/simulation_results.json"
    if not path.exists():
        raise RuntimeError("Run python track1_lfm_simulation.py before generating documents")
    results = json.loads(path.read_text(encoding="utf-8"))
    current = hashlib.sha256((ROOT / "track1_lfm_simulation.py").read_bytes()).hexdigest()
    if results["source_sha256"] != current:
        raise RuntimeError("Simulation results are stale; rerun track1_lfm_simulation.py")
    return results


def result_text(template):
    """Replace explicit metric tokens; leave mathematical braces untouched."""
    r = load_results()
    tokens = {
        "SNR1": r["snr_meas_1_db"], "SNR2": r["snr_meas_2_db"],
        "BOOST": r["delta_snr_meas_db"], "WIDTH1": r["mlw_1"], "WIDTH2": r["mlw_2"],
        "CFAR1": r["cfar_margin_1"], "CFAR2": r["cfar_margin_2"],
        "CFAR_DELTA": r["cfar_margin_2"] - r["cfar_margin_1"],
        "THEORY1": r["snr_theory_1_db"], "THEORY2": r["snr_theory_2_db"],
        "MARGIN1": r["margin_1_db"], "MARGIN2": r["margin_2_db"],
        "REQUIRED": r["snr_required_db"], "PSL1": r["psl_1_db"], "PSL2": r["psl_2_db"],
        "MC_MEAN": r["monte_carlo"]["mean_boost_db"],
        "MC_LOW": r["monte_carlo"]["mean_ci95_db"][0], "MC_HIGH": r["monte_carlo"]["mean_ci95_db"][1],
    }
    for key, value in tokens.items():
        template = template.replace("{{" + key + "}}", f"{value:.2f}")
    return template
