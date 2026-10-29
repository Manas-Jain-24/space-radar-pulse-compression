# Space Radar Pulse Compression — Track 1

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
| Theoretical matched-filter SNR | 17.44 dB | 27.44 dB |
| Noisy peak / known output-noise variance | 17.13 dB | 27.31 dB |
| Noisy half-power width | 35.36 m | 34.17 m |
| Noisy profile sidelobe statistic | -10.49 dB | -11.89 dB |
| Theoretical link margin | 4.25 dB | 14.25 dB |
| Local CA-CFAR target margin | 4.14 dB | 10.08 dB |

Seed 2026: SNR gain **10.18 dB**. Theoretical gain: 10.00 dB.
200 trials of the production echo/filter functions: mean **9.99 dB**, approximate 95% confidence interval for the mean **[9.88, 10.10] dB**.
<!-- computed-results:end -->

Nominal range resolution c/(2B) = 37.5 m. This is different from the full half-power width of a sinc-squared response (approximately 33.2 m in the large-TB limit).
The table uses a noisy single realization, so its widths and sidelobes are not noise-free waveform specifications.
Link margin subtracts the 13.18 dB required SNR for a nonfluctuating single-cell detector with Pd=0.9 and Pfa=1e-6.
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
