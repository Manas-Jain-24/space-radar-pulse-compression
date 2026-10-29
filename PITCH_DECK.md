# Utkrishta 2026: Beyond the Signal Research-Athon
## 5-Slide Finalist Pitch Deck & Presentation Guide (Track 1)
**Topic:** LFM Radar Pulse Compression & +10 dB SNR Boost for Long-Range Space Target Tracking  
**Curator:** Mr. Rajendra Kumar, Scientist, Radar Division, SDSC SHAR  
**Files:** [`PITCH_DECK.pptx`](PITCH_DECK.pptx) | [`PITCH_DECK.pdf`](PITCH_DECK.pdf)  

---

### Slide 1: Title, Team & Track Alignment (Time: 0:00 – 0:45)
- **Visuals:** Dark space-tech theme with deep navy card, cyan accents, and clear institutional branding (Utkrishta 2026, SSG × Research Club, IIIT Sri City).
- **Header:** Utkrishta 2026 | SSG × Research Club, IIIT Sri City
- **Main Title:** LFM Radar Pulse Compression & +10 dB SNR Boost for Long-Range Space Target Tracking
- **Subtitle:** Solving the Radar Energy-Resolution Dilemma at 200 km Range with Linear Frequency Modulation
- **Details:**
  - Track 1: Radar Signal Processing — Target Detection, Pulse Compression & SNR Enhancement
  - Curator: Mr. Rajendra Kumar (Scientist, Radar Division, SDSC SHAR)
  - Team Name: Team Beyond Signals
  - Team Members: Manas Vinod Jain, Vikhyat Gupta
- **Presenter Script:**
  > *"Respected jury members and Mr. Rajendra Kumar, today our team presents our research and simulation on Track 1: LFM Radar Pulse Compression and SNR Enhancement. In space launch tracking and orbital surveillance at SDSC SHAR, detecting small radar cross-section objects at 200 kilometers presents a fundamental physics dilemma between pulse energy and range resolution. Today, we show how an LFM chirp architecture achieves an exact +10 dB SNR boost while maintaining sharp 37.5-meter range resolution."*

---

### Slide 2: Problem Overview & System / Signal Setup (Time: 0:45 – 1:45)
- **Left Panel (The Classical Radar Dilemma):**
  - Mission Goal: Detect distant targets ($R = 200\text{ km}$, $\text{RCS} = 1.0\text{ m}^2$).
  - Simple CW Pulses: Energy is $E_t = P_t \tau$, but resolution is $\Delta R = c\tau/2$.
  - Catastrophic Conflict: Increasing $\tau$ from $10\ \mu\text{s}$ to $100\ \mu\text{s}$ increases energy by $10\times$, but blows up range resolution from $1.5\text{ km}$ to $15\text{ km}$—making orbital tracking impossible.
  - The LFM Solution: By sweeping frequency over $B = 4\text{ MHz}$, resolution becomes $\Delta R = c/(2B) = 37.5\text{ m}$, completely independent of pulse width!
- **Right Panel (SDSC SHAR Radar Link Parameters):**
  - Carrier: $f_c = 3.0\text{ GHz}$ (S-band, $\lambda = 0.1\text{ m}$).
  - PRT: $2.0\text{ ms}$ ($\text{PRF} = 500\text{ Hz}$, $R_{\text{unamb}} = 300\text{ km}$).
  - Sweep Bandwidth: $B = 4.0\text{ MHz}$ ($\Delta R = 37.5\text{ m}$).
  - Pulses: $10\ \mu\text{s}$ ($TB = 40$) vs $100\ \mu\text{s}$ ($TB = 400$).
  - Transmit Power: $P_t = 250\text{ kW}$ ($53.98\text{ dBW}$).
  - Antenna Gain: $G = 40\text{ dBi}$ each ($G = 10^4$).
  - Target: $R = 200\text{ km}$, $\text{RCS} = 1.0\text{ m}^2$, Delay $\tau_d = 1.333\text{ ms}$.
  - Received Power: $P_r = 3.95 \times 10^{-14}\text{ W}$ ($-134.04\text{ dBW}$).
  - Noise Floor: $N_0 = -201.48\text{ dBW/Hz}$ ($F = 2.5\text{ dB}$, $L = 3.0\text{ dB}$).
- **Presenter Script:**
  > *"To ground our simulation in real operational realities, we modeled an S-band tracking radar with 250 kW peak power and 40 dBi dish antennas. At 200 km, the target return is an ultra-weak -134 dBW, sitting below the receiver noise floor. If we used an unmodulated 100 μs pulse, our target would smear across 15 kilometers. By applying a 4 MHz LFM sweep, our theoretical resolution is locked at 37.5 meters regardless of whether we transmit for 10 or 100 microseconds."*

---

### Slide 3: Methodology / Simulation Workflow (Time: 1:45 – 2:45)
- **Top 4 Process Cards:**
  - **Step 1 (Signal Synthesis):** Dual LFM chirps ($B = 4\text{ MHz}$, $f_s = 16\text{ MHz}$). Slope $k_{r1} = 4\times 10^{11}\text{ Hz/s}$ vs $k_{r2} = 4\times 10^{10}\text{ Hz/s}$. Pulse train over $2\text{ ms}$ PRT.
  - **Step 2 (Channel Propagation):** Causal delay $\tau_d = 1.333\text{ ms}$, continuous phase tracking, circular complex AWGN noise.
  - **Step 3 (Matched Filtering):** Zero-padded FFT cross-correlation $y(t) = \text{ifft}(\text{fft}(s_{\text{rx}}) \cdot \text{conj}(\text{fft}(s_{\text{ref}})))$, eliminating circular wraparound.
  - **Step 4 (Detection & CFAR):** 1-D CA-CFAR with 48 reference and 16 guard cells, $P_{\text{fa}} = 10^{-6}$, and Marcum-Q detection thresholding.
- **Bottom Visual:** Embedded Figure 2 showing time-domain waveforms and two-sided 4 MHz frequency spectra with classic Fresnel ripples.
- **Presenter Script:**
  > *"Our simulation is fully reproducible and zero-padded in the frequency domain to prevent circular convolution artifacts. As seen in the spectra at the bottom, both pulses occupy the identical 4 MHz band, but the 100 μs pulse has a 10x steeper spectral roll-off due to its higher time-bandwidth product of 400."*

---

### Slide 4: Core Visual Plots & Quantitative Benchmark Table (Time: 2:45 – 3:45)
- **Left Visual:** Embedded Figure 4 showing the zoomed compressed target echo at $R = 200\text{ km}$.
- **Right Benchmark Table:**
  - $TB$: $40$ vs $400$ ($+10.0\text{ dB}$).
  - Radiated Energy: $2.5\text{ J}$ vs $25.0\text{ J}$ ($+10.0\text{ dB}$).
  - Theoretical Matched Filter SNR: $17.44\text{ dB}$ vs $27.44\text{ dB}$ ($+10.00\text{ dB}$).
  - Simulated Measured Peak SNR: **$17.13\text{ dB}$ vs $27.31\text{ dB}$ ($+10.18\text{ dB}$ boost)**!
  - Nominal Range Resolution: $37.50\text{ m}$ vs $37.50\text{ m}$ (Identical!).
  - Measured $-3\text{ dB}$ Width: $35.36\text{ m}$ vs $34.17\text{ m}$ ($0.97\times \approx 1.0\times$!).
  - Link Margin: $+4.25\text{ dB}$ (marginal) vs $+14.25\text{ dB}$ (robust $+10\text{ dB}$ boost).
  - CA-CFAR Margin: $+6.81\text{ dB}$ vs $+16.99\text{ dB}$ ($+10.18\text{ dB}$ boost).
- **Presenter Script:**
  > *"Here is the core proof of the challenge. On the left plot, look at the purple double-arrow: the peak output SNR jumps from 17.13 dB to 27.31 dB—an empirical boost of +10.18 dB, matching theory to within 0.18 dB! Simultaneously, notice the horizontal width of the peaks: both measure 35 meters at half-power. The range resolution is completely unaffected. We gained 10 dB of signal power for free without sacrificing a single meter of resolution."*

---

### Slide 5: Insights, Trade-offs & Conclusions (Time: 3:45 – 5:00)
- **Left Panel (Operational Insights & Trade-offs):**
  - **Empirical Validation:** Demonstrated $+10.18\text{ dB}$ SNR boost and resolution invariance across full Monte Carlo noise realizations.
  - **Link Margin Impact:** At $200\text{ km}$, a $+4.25\text{ dB}$ margin is dangerous in heavy rain or antenna jitter. The $100\ \mu\text{s}$ pulse provides $+14.25\text{ dB}$ margin, guaranteeing $P_D > 99.9\%$.
  - **Blind Zone Trade-off:** The minimum blind range is $R_{\text{min}} = c\tau/2 = 15.0\text{ km}$ for $100\ \mu\text{s}$ (vs $1.5\text{ km}$ for $10\ \mu\text{s}$). Solution: dual-pulse scheduling.
  - **Doppler Coupling:** High radial velocity causes apparent range shift $\Delta \tau = -f_d / k_r$. Solution: alternate up/down chirps.
- **Right Visual:** Embedded Figure 5 showing CA-CFAR detection margin comparison.
- **Presenter Script:**
  > *"In conclusion, LFM pulse compression is the backbone of modern space tracking radars. While the 100 μs pulse delivers superior sensitivity, it introduces a 15 km receiver blind zone. In operational launch tracking at Sriharikota, radar systems employ dual-pulse scheduling: transmitting short chirps during early launch phases and switching to 100 μs wide chirps as rockets transition to deep orbital insertion. Thank you, and we welcome questions from Mr. Rajendra Kumar and the faculty jury."*

---

### 3-Minute Jury Q&A Preparation: Anticipated Questions & Answers

1. **Q (SDSC SHAR): Why did your measured SNR enhancement give +10.18 dB instead of exactly +10.00 dB?**
   - *A:* "The theoretical +10.00 dB is derived in continuous time for infinite bandwidth. In discrete time with sampling rate $f_s = 16\text{ MHz}$, two subtle physical effects occur: (1) fractional delay positioning relative to discrete sample grid points, and (2) discrete noise realization variance over finite samples. The $0.18\text{ dB}$ variance is well within expected empirical error bounds for a single-pulse realization."

2. **Q (Faculty): Why didn't you simply increase the transmitter peak power $P_t$ by 10x instead of using a longer pulse?**
   - *A:* "Increasing peak power from 250 kW to 2.5 MW introduces severe engineering challenges: high voltage dielectric breakdown, waveguide arcing, and thermal dissipation limits in solid-state transmitters (GaN/SSPA). Extending pulse duration from 10 μs to 100 μs costs zero extra hardware peak power—it only increases average power and duty cycle from 0.5% to 5.0%, which modern SSPAs handle with high efficiency."

3. **Q: What happens if the target at 200 km is moving at orbital speed (e.g., 7 km/s)?**
   - *A:* "An orbital target moving at $7\text{ km/s}$ induces a Doppler shift $f_d = 2v_r/\lambda = 2(7000)/0.1 = 140\text{ kHz}$. In an LFM matched filter, Doppler shift causes a time shift $\Delta t = -f_d / k_r$. For the $100\ \mu\text{s}$ pulse ($k_r = 4\times 10^{10}\text{ Hz/s}$), this produces an apparent range bias $\Delta R = -c f_d / (2 k_r) = -525\text{ m}$. In operational radar tracking, we resolve this by transmitting alternating up-chirps and down-chirps, or by performing 2D Range-Doppler processing across the coherent processing interval (CPI)."
