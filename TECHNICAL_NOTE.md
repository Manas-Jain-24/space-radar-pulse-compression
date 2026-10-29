# Technical Note — Track 1
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
| Theoretical SNR | 17.44 dB | 27.44 dB |
| Noisy peak statistic | 17.13 dB | 27.31 dB |
| Half-power width | 35.36 m | 34.17 m |
| Link margin | 4.25 dB | 14.25 dB |
| CA-CFAR margin | 4.14 dB | 10.08 dB |

Baseline SNR gain: 10.18 dB. CA-CFAR margin difference: 5.93 dB; this is not the SNR gain.
200 production-chain trials: mean gain 9.99 dB; approximate 95% CI for the mean [9.88, 10.10] dB.
The theoretical required SNR is 13.18 dB for Pd=0.9, Pfa=1e-6, a nonfluctuating single-cell target and known Gaussian-noise statistics.

## 4. Takeaways and limitations
LFM preserves fine nominal resolution while a longer pulse supplies ten times the energy. Average transmit power also increases tenfold.
Nominal 37.5 m resolution is not the same definition as full half-power width; noisy width/PSL measurements vary with realization.
The 100 µs transmit blind range is 15 km. Doppler causes range bias. Windowing trades SNR/width for sidelobe suppression.
CFAR probability calibration assumes independent exponential cells, unlike the correlated oversampled matched-filter output.
The study does not establish field detection probabilities, operational reliability or actual SDSC SHAR equipment characteristics.
