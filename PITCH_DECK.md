# Five-slide pitch guide — Track 1

## Slide 1 — Title and team (30 seconds)
LFM radar pulse compression: Team Spaceship, Manas Vinod Jain and Vikhyat Gupta. State the 200 km point-target challenge.

## Slide 2 — Setup (60 seconds)
Compare 10/100 µs pulses, PRT=2 ms and B=4 MHz. Explain the assumed S-band link parameters.
Tenfold energy raises average power from 1.25 to 12.5 kW. Nominal compressed resolution is 37.5 m for both.

## Slide 3 — Method (60 seconds)
Waveform → range-equation echo and AWGN → zero-padded matched filter → SNR/width → CA-CFAR.
48 reference/16 guard cells total. Distinguish the required input SNR for a target Pd from the power-statistic threshold.

## Slide 4 — Evidence (90 seconds)
Seed-2026 peak statistics: 17.13 and 27.31 dB; difference 10.18 dB.
Noisy widths: 35.36/34.17 m. Link margins: 4.25/14.25 dB.
Local CFAR margins: 4.14/10.08 dB; their difference is 5.93 dB.
200 production-chain trials: mean 9.99 dB, 95% mean CI [9.88, 10.10] dB.

## Slide 5 — Insights and limitations (60 seconds)
Show the two-target and up/down-chirp studies. Explain the 15 km long-pulse blind zone, energy cost and Doppler coupling.
State that CA-CFAR nominal Pfa assumes independent cells; oversampled output is correlated. Do not promise zero false alarms or field reliability.

## Jury questions
- Why isn't one realization exactly +10 dB? Noise and fractional-bin placement affect the peak statistic; the multi-seed mean supports theory.
- Is the gain free? No: pulse energy, duty cycle and average transmit power increase tenfold.
- Are these actual SDSC SHAR parameters? They are explicitly assumed representative link values.
- Does NLFM achieve −35 dB? This tangent design measures approximately −29.30 dB; the Taylor-weighted LFM measures approximately −34.64 dB.
- Is the HTML page the experiment? It is an analytical calculator with illustrative curves; the Python code supplies numerical evidence.
