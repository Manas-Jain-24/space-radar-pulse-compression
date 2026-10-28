# Space Radar Pulse Compression & SNR Enhancement Simulation

> **Beyond the Signal: Radar Systems & Applied Space-Tech 24-Hour Research-Athon (Utkrishta 2026)**  
> **Track 1:** Radar Signal Processing — Target Detection, Pulse Compression & SNR Enhancement  
> **Curated by:** Mr. Rajendra Kumar, Scientist, Radar Division, Satish Dhawan Space Centre (SDSC SHAR), ISRO  
> **Organized by:** Student Satellite Group (SSG) × Research Club, IIIT Sri City  

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Manas-Jain-24/space-radar-pulse-compression/blob/main/track1_radar_notebook.ipynb)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen?logo=github&style=flat)](https://manas-jain-24.github.io/space-radar-pulse-compression/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Quick-Access Deliverables

All mandatory deliverables for the **October 29 (6:00 PM)** submission freeze are ready and verifiable:

| Deliverable | File Link | Format | Description |
| :--- | :--- | :--- | :--- |
| **Core Simulation Script** | [`track1_lfm_simulation.py`](track1_lfm_simulation.py) | Python | End-to-end radar chain ($R=200\text{ km}$, $\text{PRT}=2\text{ ms}$, $B=4\text{ MHz}$, $+10.18\text{ dB}$ SNR proof) |
| **Bonus Upgrades Script** | [`track1_bonus_upgrades.py`](track1_bonus_upgrades.py) | Python | Multi-target 50m resolution, Mach 5 Doppler coupling, and Taylor windowing |
| **Interactive Colab Notebook** | [`track1_radar_notebook.ipynb`](track1_radar_notebook.ipynb) | Jupyter / Colab | Standalone, 1-click runnable notebook with markdown explanations |
| **2-Page Technical Note (PDF)** | [`TECHNICAL_NOTE_IEEE.pdf`](TECHNICAL_NOTE_IEEE.pdf) | PDF (2 Pages) | Official IEEE 2-column research report with math, tables & embedded figures |
| **2-Page Technical Note (Markdown)** | [`TECHNICAL_NOTE.md`](TECHNICAL_NOTE.md) | Markdown | Complete GitHub-rendered report with Mermaid processing pipeline |
| **5-Slide Finalist Pitch Deck (PDF)**| [`PITCH_DECK.pdf`](PITCH_DECK.pdf) | PDF (16:9) | High-resolution widescreen slide deck for jury presentation |
| **5-Slide Finalist Pitch Deck (PPTX)**| [`PITCH_DECK.pptx`](PITCH_DECK.pptx) | PPTX (16:9) | Editable PowerPoint presentation deck with space-tech theme |
| **Presentation & Defense Guide** | [`PITCH_DECK.md`](PITCH_DECK.md) | Markdown | 5-minute slide-by-slide script and 3-minute jury Q&A defense answers |
| **Live Interactive Dashboard** | [**Live Web Demo**](https://manas-jain-24.github.io/space-radar-pulse-compression/) ([`dashboard.html`](dashboard.html)) | Web (GitHub Pages) | Standalone, zero-install radar oscilloscope GUI with real-time sliders |
| **Streamlit Web Application** | [`app.py`](app.py) | Python / Streamlit | Live reactive web dashboard with Matplotlib and CA-CFAR controls |
| **Advanced Engineering Suite** | [`advanced_upgrade1_ambiguity.py`](advanced_upgrade1_ambiguity.py) to [`upgrade5`](advanced_upgrade5_hardware_imperfections.py) | Python (5 Modules) | Ambiguity function, CFAR family (GO/SO/OS), CPI Range-Doppler, NLFM, & ADC realism |
| **Complete Submission Archive** | [`submission_bundle.zip`](submission_bundle.zip) | ZIP Archive (15.9 MB) | Standalone all-in-one archive containing all PDFs, PPTX, scripts, and figures |
| **Publication-Ready Figures** | [`figures/track1/`](figures/track1/) | 13 PNGs (300 DPI)| High-resolution plots for all core tasks and advanced experiments |

---

## 2. Executive Summary & Physics Formulation

In long-range space launch tracking and ballistic surveillance at SDSC SHAR, detecting distant, small radar cross-section objects ($R = 200\text{ km}$, $\text{RCS} = 1.0\text{ m}^2$) requires high radiated pulse energy:
$$E_t = P_t \cdot \tau_p$$

For simple unmodulated rectangular continuous-wave (CW) pulses, range resolution is tied to pulse duration:
$$\Delta R_{\text{unmod}} = \frac{c \cdot \tau_p}{2}$$

Widening an unmodulated pulse from $10\ \mu\text{s}$ to $100\ \mu\text{s}$ increases energy by $10\times$ ($+10\text{ dB}$), but severely degrades range resolution from $1.5\text{ km}$ to **$15.0\text{ km}$**—making precision tracking and target discrimination impossible.

### The LFM Pulse Compression Solution
By sweeping carrier frequency across bandwidth $B = 4.0\text{ MHz}$ within pulse duration $\tau_p$:
$$s(t) = \text{rect}\left(\frac{t}{\tau_p}\right) \exp\left(j \pi k_r t^2\right), \quad k_r = \frac{B}{\tau_p}$$

The matched filter impulse response $h(t) = s^*(-t)$ compresses the echo into a sinc envelope whose Rayleigh $-3\text{ dB}$ range resolution is governed **exclusively by bandwidth $B$**:
$$\Delta R = \frac{c}{2B} = \frac{3.0 \times 10^8\text{ m/s}}{2 \times 4.0 \times 10^6\text{ Hz}} = \mathbf{37.5\text{ m}} \quad \text{(Identical for both } 10\ \mu\text{s} \text{ and } 100\ \mu\text{s)}$$

Because the matched filter integrates total received echo energy $E_r = P_r \cdot \tau_p$, the output peak SNR scales strictly with pulse width:
$$\Delta \text{SNR}_{\text{MF}} = 10 \log_{10}\left(\frac{\tau_2}{\tau_1}\right) = 10 \log_{10}\left(\frac{100\ \mu\text{s}}{10\ \mu\text{s}}\right) = \mathbf{+10.00\text{ dB}}$$

---

## 3. SDSC SHAR Radar Link Budget & Specifications

| Parameter | Symbol | Value | Operational Note |
| :--- | :--- | :--- | :--- |
| **Carrier Frequency** | $f_c$ | $3.0\text{ GHz}$ ($\lambda = 0.1\text{ m}$) | S-band space-tracking radar |
| **Pulse Repetition Time** | $\text{PRT}$ | $2.0\text{ ms}$ ($\text{PRF} = 500\text{ Hz}$) | Unambiguous range $R_{\text{unamb}} = 300\text{ km}$ |
| **Chirp Sweep Bandwidth**| $B$ | $4.0\text{ MHz}$ | Nominal range resolution $\Delta R = 37.5\text{ m}$ |
| **Pulse Width 1** | $\tau_1$ | $10.0\ \mu\text{s}$ ($TB = 40$) | Short pulse (Duty cycle $0.5\%$, Energy $2.5\text{ J}$) |
| **Pulse Width 2** | $\tau_2$ | $100.0\ \mu\text{s}$ ($TB = 400$) | Long pulse (Duty cycle $5.0\%$, Energy $25.0\text{ J}$) |
| **Transmit Peak Power** | $P_t$ | $250.0\text{ kW}$ ($53.98\text{ dBW}$) | Typical solid-state space tracking amplifier |
| **Antenna Gain (Tx & Rx)**| $G$ | $40.0\text{ dBi}$ each ($G = 10^4$) | High-gain parabolic tracking reflector |
| **Target Range & RCS** | $R_0, \sigma$ | $200.0\text{ km}, 1.0\text{ m}^2$ | Target round-trip delay $\tau_d = 1.333\text{ ms}$ |
| **Received Target Power**| $P_r$ | $3.95 \times 10^{-14}\text{ W}$ ($-134.04\text{ dBW}$) | Calculated via Monostatic Radar Range Equation |
| **Noise Spectral Density**| $N_0$ | $7.12 \times 10^{-21}\text{ W/Hz}$ ($-201.48\text{ dBW/Hz}$) | Receiver noise figure $F = 2.5\text{ dB}$ |
| **Two-Way System Losses**| $L$ | $3.0\text{ dB}$ | Atmospheric attenuation and line losses |
| **Sampling Frequency** | $f_s$ | $16.0\text{ MHz}$ ($4 \times B$) | Range bin spacing $\delta r = 9.375\text{ m}$ |

---

## 4. Quantitative Results & Benchmark Table

| Metric / Parameter | Pulse 1 ($\tau_1 = 10\ \mu\text{s}$) | Pulse 2 ($\tau_2 = 100\ \mu\text{s}$) | Enhancement / Ratio |
| :--- | :--- | :--- | :--- |
| **Radiated Pulse Energy** | $2.50\text{ J}$ | $25.00\text{ J}$ | $\mathbf{+10.0\text{ dB}}$ |
| **Time-Bandwidth Product ($TB$)** | $40.0$ ($16.02\text{ dB}$) | $400.0$ ($26.02\text{ dB}$) | $\mathbf{+10.0\text{ dB}}$ compression gain |
| **Theoretical Matched-Filter SNR** | $17.44\text{ dB}$ | $27.44\text{ dB}$ | $\mathbf{+10.00\text{ dB}}$ |
| **Simulated Measured Peak SNR** | **$17.13\text{ dB}$** | **$27.31\text{ dB}$** | $\mathbf{+10.18\text{ dB}}$ (**Matches theory**) |
| **Nominal Range Resolution** | $37.50\text{ m}$ | $37.50\text{ m}$ | **Identical ($1.00\times$)** |
| **Measured Half-Power ($-3\text{ dB}$) Width** | $35.36\text{ m}$ | $34.17\text{ m}$ | **$0.97\times$ (Resolution Preserved)** |
| **Peak Sidelobe Level (PSL)** | $-10.49\text{ dB}$ | $-11.89\text{ dB}$ | Sampled sinc response |
| **Required Detection SNR ($P_D=0.9, P_{\text{fa}}=10^{-6}$)**| $13.18\text{ dB}$ | $13.18\text{ dB}$ | Swerling 0 Marcum Q model |
| **Theoretical Link Margin** | $+4.25\text{ dB}$ (marginal) | $\mathbf{+14.25\text{ dB}}$ (robust) | $\mathbf{+10.00\text{ dB}}$ margin boost |
| **Adaptive CA-CFAR Target Margin**| $+6.81\text{ dB}$ | $\mathbf{+16.99\text{ dB}}$ | $\mathbf{+10.18\text{ dB}}$ above adaptive threshold |

![Pulse Compression SNR Boost](figures/track1/fig4_pulse_compression_snr_boost.png)

---

## 5. Bonus Space Radar Research Experiments

To demonstrate deep operational radar engineering, three advanced experiments are implemented in [`track1_bonus_upgrades.py`](track1_bonus_upgrades.py):

### Bonus 1: Multi-Target Resolution Demonstration (50 m Separation at 200 km)
- **Scenario:** Two space objects separated by 50 meters ($R_1 = 200.000\text{ km}$, $R_2 = 200.050\text{ km}$).
- **Comparison:**
  - An unmodulated $100\ \mu\text{s}$ CW pulse smears both targets into a single $15\text{ km}$ blob.
  - The $100\ \mu\text{s}$ LFM chirp cleanly resolves **two distinct peaks separated by 50 meters**!
- **Plot:** [`figures/track1/fig6_multitarget_resolution.png`](figures/track1/fig6_multitarget_resolution.png)

![Multi-Target Resolution](figures/track1/fig6_multitarget_resolution.png)

---

### Bonus 2: Mach 5 Doppler Coupling & Chirp Diversity Ambiguity Resolution
- **Scenario:** Space launch vehicle ascending at $v_r = 1500\text{ m/s}$ (Mach 5.0, Doppler $f_d = 30\text{ kHz}$).
- **Physics:** Range-Doppler coupling shifts the apparent peak by $\Delta R = -c f_d / (2 k_r) = -112.5\text{ m}$ (3 resolution cells!).
- **Chirp Diversity Solution:** Transmitting alternating Up-Chirps and Down-Chirps decouples range and Doppler:
  $$R_{\text{estimated}} = \frac{R_{\text{up}} + R_{\text{down}}}{2} = \mathbf{199.9969\text{ km}} \quad (\text{error: only } -3.1\text{ m!})$$
  $$v_{r,\text{extracted}} = \frac{k_r \lambda (R_{\text{down}} - R_{\text{up}})}{2c} = \mathbf{1500.0\text{ m/s}} \quad (\text{exact velocity extracted!})$$
- **Plot:** [`figures/track1/fig7_doppler_coupling_and_chirp_diversity.png`](figures/track1/fig7_doppler_coupling_and_chirp_diversity.png)

---

### Bonus 3: Sidelobe Suppression & Weak Target Unmasking (Taylor & Hann)
- **Scenario:** Strong rocket body ($\text{RCS} = 5.0\text{ m}^2$) at $200.000\text{ km}$ and a faint satellite ($\text{RCS} = 0.05\text{ m}^2$, $20\text{ dB}$ weaker) at $200.080\text{ km}$.
- **Result:**
  - Under Rectangular weighting, the strong target's $-13.3\text{ dB}$ sidelobe completely buries the faint satellite.
  - Applying Taylor weighting ($\bar{n}=4, \text{SLL}=35\text{ dB}$) suppresses sidelobes to $-35.0\text{ dB}$, **cleanly unmasking the weak target** with only $-0.91\text{ dB}$ SNR loss!
- **Plot:** [`figures/track1/fig8_windowing_sidelobe_suppression.png`](figures/track1/fig8_windowing_sidelobe_suppression.png)

---

### Advanced Upgrade 1: Woodward Ambiguity Function & 3D Delay-Doppler Surface
- **Script:** [`advanced_upgrade1_ambiguity.py`](advanced_upgrade1_ambiguity.py)
- **Physics:** Rigorous evaluation of the matched filter response $|\chi(\tau, \nu)|^2$ in range and velocity dimensions.
- **Result:** Maps the signature sheared diagonal ridge ($\nu + k_r \tau = 0$) proving Doppler tolerance, volume invariance ($\iint |\chi|^2 = 1$), and 40x compression over unmodulated pulses.
- **Plot:** [`figures/track1/fig9_ambiguity_function_3d_and_contours.png`](figures/track1/fig9_ambiguity_function_3d_and_contours.png)

---

### Advanced Upgrade 2: Advanced CFAR Family Comparison (CA vs. GO vs. SO vs. OS)
- **Script:** [`advanced_upgrade2_cfar_family.py`](advanced_upgrade2_cfar_family.py)
- **Scenario A (Multi-Target Masking):** In close spacecraft clusters, CA-CFAR threshold is inflated by Target 1, burying Target 2. **SO-CFAR** drops the threshold, detecting both targets cleanly!
- **Scenario B (Clutter Boundary Step):** Crossing a $+15\text{ dB}$ clutter edge triggers massive CA-CFAR false alarm bursts. **GO-CFAR** clamps the threshold to the maximum, regulating $P_{\text{fa}} = 10^{-5}$ perfectly!
- **Plot:** [`figures/track1/fig10_cfar_family_comparison.png`](figures/track1/fig10_cfar_family_comparison.png)

---

### Advanced Upgrade 3: Coherent Processing Interval (CPI) over M=32 Pulses & 2D Range-Doppler Map
- **Script:** [`advanced_upgrade3_coherent_range_doppler.py`](advanced_upgrade3_coherent_range_doppler.py)
- **Physics:** Fast-Time / Slow-Time 2D data cube processing over $M = 32$ coherent pulses ($64\text{ ms}$ dwell).
- **Result:** Coherent integration yields an **additional $+10 \log_{10}(32) = \mathbf{+15.05\text{ dB}}$ SNR enhancement** (total system gain $+41.07\text{ dB}$), while cleanly separating ascending vehicles ($v_r = 1500\text{ m/s}$) from stationary ground/sea clutter at Doppler bin 0!
- **Plot:** [`figures/track1/fig11_coherent_range_doppler_map.png`](figures/track1/fig11_coherent_range_doppler_map.png)

---

### Advanced Upgrade 4: Nonlinear FM (NLFM) Waveform Design (0.00 dB Mismatch Loss)
- **Script:** [`advanced_upgrade4_nlfm_waveform.py`](advanced_upgrade4_nlfm_waveform.py)
- **The Breakthrough:** Windowing (Taylor) reduces sidelobes to $-35\text{ dB}$ but suffers $-0.91\text{ dB}$ SNR mismatch loss. By sweeping instantaneous frequency along a tangent curve, **NLFM achieves $-35.0\text{ dB}$ low sidelobes with ZERO ($0.00\text{ dB}$) SNR mismatch loss**, maintaining constant envelope!
- **Plot:** [`figures/track1/fig12_nlfm_waveform_vs_lfm.png`](figures/track1/fig12_nlfm_waveform_vs_lfm.png)

---

### Advanced Upgrade 5: Receiver Hardware Realism (ADC Bits, Phase Jitter & I/Q Imbalance)
- **Script:** [`advanced_upgrade5_hardware_imperfections.py`](advanced_upgrade5_hardware_imperfections.py)
- **Findings:**
  - **ADC Quantization:** Matched filter process gain ($+32\text{ dB}$) digs weak signals out even below the ADC LSB; 10-bit and 12-bit ADCs match ideal 64-bit float SNR to within $0.05\text{ dB}$!
  - **LO Phase Noise:** Phase jitter $\le 5^\circ$ preserves $-35\text{ dB}$ sidelobes; excessive jitter ($>15^\circ$) elevates the sidelobe noise pedestal.
  - **I/Q Imbalance:** Models quadrature gain and phase skew, demonstrating digital calibration requirements.
- **Plot:** [`figures/track1/fig13_receiver_hardware_imperfections.png`](figures/track1/fig13_receiver_hardware_imperfections.png)

---

## 6. How to Run & Reproduce

### Running in Google Colab (Zero Installation)
Click the badge at the top or open:
👉 **[Open in Google Colab](https://colab.research.google.com/github/Manas-Jain-24/space-radar-pulse-compression/blob/main/track1_radar_notebook.ipynb)**

### Running Locally
```bash
# 1. Clone the repository
git clone https://github.com/Manas-Jain-24/space-radar-pulse-compression.git
cd space-radar-pulse-compression

# 2. Set up virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Core Simulation (Generates Figs 1 to 5)
python track1_lfm_simulation.py

# 5. Run Bonus Upgrades (Generates Figs 6, 7, 8)
python track1_bonus_upgrades.py

# 6. Run Advanced Engineering Suite (Generates Figs 9 to 13)
python advanced_upgrade1_ambiguity.py
python advanced_upgrade2_cfar_family.py
python advanced_upgrade3_coherent_range_doppler.py
python advanced_upgrade4_nlfm_waveform.py
python advanced_upgrade5_hardware_imperfections.py

# 7. (Optional) Regenerate Technical Note PDF & Finalist Pitch Deck
python scripts/generate_pdf_report.py
python scripts/generate_pitch_deck.py
python scripts/generate_pitch_deck_pdf.py

# 7. Launch Interactive Radar Dashboard
# Option A: Zero-install HTML5 GUI (Double-click dashboard.html or serve locally)
python -m http.server 8501
# Open in browser: http://localhost:8501/dashboard.html

# Option B: Streamlit Web Application
pip install streamlit
streamlit run app.py
```

---

## 7. Team & Acknowledgements
- **Team Name:** Team Beyond Signals
- **Event:** Beyond the Signal: Radar Systems & Applied Space-Tech 24-Hour Research-Athon (Utkrishta 2026)
- **Organized by:** Student Satellite Group (SSG) × Research Club, Indian Institute of Information Technology (IIIT) Sri City
- **Track Curator:** Mr. Rajendra Kumar, Scientist, Radar Division, Satish Dhawan Space Centre (SDSC SHAR), ISRO
