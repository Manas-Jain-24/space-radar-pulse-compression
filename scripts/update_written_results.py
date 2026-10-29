"""Regenerate the written submission from the same computed baseline as the PDFs."""
from pathlib import Path
from report_data import ROOT, result_text


def update_written_results():
    readme = r"""# Space Radar Pulse Compression — Track 1

Team Spaceship: Manas Vinod Jain, Vikhyat Gupta. Utkrishta 2026, SSG × Research Club, IIIT Sri City.

## Problem and implementation

Compare 10 µs and 100 µs LFM up-chirps at 4 MHz bandwidth, 2 ms PRT, and the same peak transmit power.
The target is at 200 km with RCS 1 m². The pipeline generates waveforms and a pulse train, calculates a monostatic link budget,
adds delayed echoes and complex AWGN, applies zero-padded FFT correlation, and measures SNR, width and CA-CFAR margin.

The 3 GHz carrier, 250 kW peak power, 40 dBi gains, 2.5 dB noise figure, 290 K temperature and 3 dB losses are **simulation assumptions**.
They are not verified SDSC SHAR equipment specifications. Sampling is 16 MHz (9.375 m range-bin spacing).

## Computed baseline

<!-- computed-results:start -->
| Metric | 10 µs | 100 µs |
|---|---:|---:|
| Pulse energy | 2.50 J | 25.00 J |
| Theoretical matched-filter SNR | {{THEORY1}} dB | {{THEORY2}} dB |
| Noisy peak / known output-noise variance | {{SNR1}} dB | {{SNR2}} dB |
| Noisy half-power width | {{WIDTH1}} m | {{WIDTH2}} m |
| Noisy profile sidelobe statistic | {{PSL1}} dB | {{PSL2}} dB |
| Theoretical link margin | {{MARGIN1}} dB | {{MARGIN2}} dB |
| Local CA-CFAR target margin | {{CFAR1}} dB | {{CFAR2}} dB |

Seed 2026: SNR gain **{{BOOST}} dB**. Theoretical gain: 10.00 dB.
200 trials of the production echo/filter functions: mean **{{MC_MEAN}} dB**, approximate 95% confidence interval for the mean **[{{MC_LOW}}, {{MC_HIGH}}] dB**.
<!-- computed-results:end -->

Nominal range resolution c/(2B) = 37.5 m. This is different from the full half-power width of a sinc-squared response (approximately 33.2 m in the large-TB limit).
The table uses a noisy single realization, so its widths and sidelobes are not noise-free waveform specifications.
Link margin subtracts the {{REQUIRED}} dB required SNR for a nonfluctuating single-cell detector with Pd=0.9 and Pfa=1e-6.
CA-CFAR uses 24 reference and eight guard cells **per side** (48/16 total). Its nominal Pfa formula assumes independent exponential cells;
oversampled matched-filter cells are correlated, and sidelobes can contaminate the reference window. No zero-false-alarm guarantee is made.

## Reproduce locally

Use Python 3.10+:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python track1_lfm_simulation.py
python track1_bonus_upgrades.py
python advanced_upgrade1_ambiguity.py
python advanced_upgrade2_cfar_family.py
python advanced_upgrade3_coherent_range_doppler.py
python advanced_upgrade4_nlfm_waveform.py
python advanced_upgrade5_hardware_imperfections.py
python scripts/update_written_results.py
python scripts/generate_pdf_report.py
python scripts/generate_pitch_deck.py
python scripts/generate_pitch_deck_pdf.py
python -m unittest discover -s tests -p test_regressions.py -v
python tests/stress_test_suite.py
python scripts/package_submission.py
```

The core writes `figures/track1/simulation_results.json`. Document generators reject results whose core-source hash is stale.
The stress suite regenerates plots/documents; package the final ZIP after it finishes.
The ZIP includes the tests, results and all required source files. Open `track1_radar_notebook.ipynb` from the repository root for the same pipeline.

## Bonus studies and their scope

- `track1_bonus_upgrades.py`: two targets 50 m apart (one measured central peak in the default coherent unequal-target case; separation is not guaranteed); up/down-chirp Doppler bias; Taylor/Hann/Hamming receiver weighting.
- `advanced_upgrade1_ambiguity.py`: analytical Woodward ambiguity surfaces; a visual study, not an integral-volume validation.
- `advanced_upgrade2_cfar_family.py`: CA/GO/SO/OS thresholds calibrated for independent exponential noise. Clutter-edge behavior is illustrative; calibration is tested in homogeneous noise.
- `advanced_upgrade3_coherent_range_doppler.py`: synthetic **post-compression** cube, 32 pulses, 125 Hz on-bin Doppler. Hann expected gain is 13.15 dB; the unwindowed ideal is 15.05 dB. It does not propagate a moving LFM pulse train.
- `advanced_upgrade4_nlfm_waveform.py`: tangent NLFM, measured PSL approximately −29.30 dB with zero matched-receiver mismatch loss; Taylor LFM approximately −34.64 dB. Widths are measured separately.
- `advanced_upgrade5_hardware_imperfections.py`: one-realization ADC sensitivity, RMS-normalized low-pass phase noise and IQ imbalance. No receiver calibration algorithm is implemented.

## Interfaces and deliverables

`index.html` / `dashboard.html` are a theoretical link-budget calculator with **illustrative** curves. They do not run the Python simulation or measure CFAR statistics.
Serve with `python -m http.server 8501`. `streamlit run app.py` runs the separate interactive Python application.

Deliverables: `TECHNICAL_NOTE_IEEE.pdf` (two pages), `PITCH_DECK.pdf` and `PITCH_DECK.pptx` (five slides each), scripts/notebook, saved plots and `submission_bundle.zip`.

## Interpretation and limitations

The +10 dB gain costs ten times the pulse energy and average transmit power (1.25 kW → 12.5 kW at fixed PRT).
The 100 µs monostatic transmit blind range is 15 km versus 1.5 km for 10 µs; echo fit also limits the far range.
This is an ideal synthetic radar study: fixed RCS, AWGN, simplified losses and no validated atmospheric, antenna, clutter or hardware model.
High radial speed causes Doppler aliasing across pulses and range–Doppler coupling; an ideal algebraic cancellation is not a robust tracking algorithm.

References: Skolnik, *Introduction to Radar Systems*; Richards, *Fundamentals of Radar Signal Processing*;
Rohling, “Radar CFAR Thresholding in Clutter and Multiple Target Situations,” IEEE TAES (1983); supplied Track 1 handout.
"""
    note = r"""# Technical Note — Track 1
Team Spaceship: Manas Vinod Jain, Vikhyat Gupta.

## 1. Problem and mathematical formulation
For fixed peak power, pulse energy is E = Pt τ. Unmodulated nominal range resolution is cτ/2.
An LFM waveform s(t) = rect(t/τ) exp(jπ(B/τ)t²) and matched filter h(t)=s*(-t) give nominal resolution c/(2B)=37.5 m.
At equal received power, output SNR = Pr τ / N0, so 10 log10(100/10)=10 dB.
Pr = Pt Gtx Grx λ² σ / [(4π)³ R⁴ L], and N0=kTF. The complex sampled-noise variance is N0 fs.
The assumed S-band link uses 250 kW, gains 40 dBi, 3 GHz carrier, NF 2.5 dB and losses 3 dB; these are not verified equipment specifications.

## 2. Methodology
PRT 2 ms → 10/100 µs, 4 MHz LFM → delayed 200 km, 1 m² point-target echoes → complex AWGN → FFT linear correlation → measurements → CA-CFAR.
Both pulses use the same noise realization for the baseline. CA-CFAR has 24 reference/eight guard cells per side.
The notebook imports the same simulation functions rather than duplicating their implementation.

## 3. Results and comparison
| Metric | 10 µs | 100 µs |
|---|---:|---:|
| Theoretical SNR | {{THEORY1}} dB | {{THEORY2}} dB |
| Noisy peak statistic | {{SNR1}} dB | {{SNR2}} dB |
| Half-power width | {{WIDTH1}} m | {{WIDTH2}} m |
| Link margin | {{MARGIN1}} dB | {{MARGIN2}} dB |
| CA-CFAR margin | {{CFAR1}} dB | {{CFAR2}} dB |

Baseline SNR gain: {{BOOST}} dB. CA-CFAR margin difference: {{CFAR_DELTA}} dB; this is not the SNR gain.
200 production-chain trials: mean gain {{MC_MEAN}} dB; approximate 95% CI for the mean [{{MC_LOW}}, {{MC_HIGH}}] dB.
The theoretical required SNR is {{REQUIRED}} dB for Pd=0.9, Pfa=1e-6, a nonfluctuating single-cell target and known Gaussian-noise statistics.

## 4. Takeaways and limitations
LFM preserves fine nominal resolution while a longer pulse supplies ten times the energy. Average transmit power also increases tenfold.
Nominal 37.5 m resolution is not the same definition as full half-power width; noisy width/PSL measurements vary with realization.
The 100 µs transmit blind range is 15 km. Doppler causes range bias. Windowing trades SNR/width for sidelobe suppression.
CFAR probability calibration assumes independent exponential cells, unlike the correlated oversampled matched-filter output.
The study does not establish field detection probabilities, operational reliability or actual SDSC SHAR equipment characteristics.
"""
    pitch = r"""# Five-slide pitch guide — Track 1

## Slide 1 — Title and team (30 seconds)
LFM radar pulse compression: Team Spaceship, Manas Vinod Jain and Vikhyat Gupta. State the 200 km point-target challenge.

## Slide 2 — Setup (60 seconds)
Compare 10/100 µs pulses, PRT=2 ms and B=4 MHz. Explain the assumed S-band link parameters.
Tenfold energy raises average power from 1.25 to 12.5 kW. Nominal compressed resolution is 37.5 m for both.

## Slide 3 — Method (60 seconds)
Waveform → range-equation echo and AWGN → zero-padded matched filter → SNR/width → CA-CFAR.
48 reference/16 guard cells total. Distinguish the required input SNR for a target Pd from the power-statistic threshold.

## Slide 4 — Evidence (90 seconds)
Seed-2026 peak statistics: {{SNR1}} and {{SNR2}} dB; difference {{BOOST}} dB.
Noisy widths: {{WIDTH1}}/{{WIDTH2}} m. Link margins: {{MARGIN1}}/{{MARGIN2}} dB.
Local CFAR margins: {{CFAR1}}/{{CFAR2}} dB; their difference is {{CFAR_DELTA}} dB.
200 production-chain trials: mean {{MC_MEAN}} dB, 95% mean CI [{{MC_LOW}}, {{MC_HIGH}}] dB.

## Slide 5 — Insights and limitations (60 seconds)
Show the two-target and up/down-chirp studies. Explain the 15 km long-pulse blind zone, energy cost and Doppler coupling.
State that CA-CFAR nominal Pfa assumes independent cells; oversampled output is correlated. Do not promise zero false alarms or field reliability.

## Jury questions
- Why isn't one realization exactly +10 dB? Noise and fractional-bin placement affect the peak statistic; the multi-seed mean supports theory.
- Is the gain free? No: pulse energy, duty cycle and average transmit power increase tenfold.
- Are these actual SDSC SHAR parameters? They are explicitly assumed representative link values.
- Does NLFM achieve −35 dB? This tangent design measures approximately −29.30 dB; the Taylor-weighted LFM measures approximately −34.64 dB.
- Is the HTML page the experiment? It is an analytical calculator with illustrative curves; the Python code supplies numerical evidence.
"""
    for name, template in (("README.md", readme), ("TECHNICAL_NOTE.md", note), ("PITCH_DECK.md", pitch)):
        (ROOT / name).write_text(result_text(template), encoding="utf-8")


if __name__ == "__main__":
    update_written_results()
