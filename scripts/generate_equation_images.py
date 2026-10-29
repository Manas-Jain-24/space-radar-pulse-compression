"""Generate crisp, high-resolution equation images for the IEEE Technical Note."""

import matplotlib.pyplot as plt
from pathlib import Path

def generate_equation_images():
    eq_dir = Path("figures/track1/equations")
    eq_dir.mkdir(parents=True, exist_ok=True)

    equations = [
        (
            "eq1_resolution.png",
            r"\Delta R_{\mathrm{unmod}} = \frac{c \tau_p}{2} \quad \longrightarrow \quad \Delta R = \frac{c}{2B} = \frac{3.0 \times 10^8\ \mathrm{m/s}}{2 \times 4.0 \times 10^6\ \mathrm{Hz}} = \mathbf{37.50\ \mathrm{m}} \qquad \mathrm{(1)}",
            9.2,
            0.36
        ),
        (
            "eq2_waveform.png",
            r"s(t) = \mathrm{rect}\left(\frac{t}{\tau_p}\right) e^{j \pi k_r t^2}, \ k_r = \frac{B}{\tau_p} \ \ \Longrightarrow \ \ y(t) = s(t) * s^*(-t) \approx \tau_p \cdot \mathrm{sinc}(\pi B t) \qquad \mathrm{(2)}",
            9.2,
            0.36
        ),
        (
            "eq3_link_budget.png",
            r"P_r = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R_0^4 L} = \frac{(250\ \mathrm{kW})(10^4)^2(0.1\ \mathrm{m})^2(1.0\ \mathrm{m}^2)}{(4\pi)^3 (200\ \mathrm{km})^4 \cdot 10^{0.3}} = 3.946 \times 10^{-14}\ \mathrm{W}\ (-134.04\ \mathrm{dBW}) \qquad \mathrm{(3)}",
            8.4,
            0.36
        ),
        (
            "eq4_snr_scaling.png",
            r"\mathrm{SNR}_{\mathrm{MF}} = \frac{P_r \tau_p}{N_0} \ \ \Longrightarrow \ \ \Delta\mathrm{SNR}_{\mathrm{MF}} = 10\log_{10}\left(\frac{\tau_2}{\tau_1}\right) = 10\log_{10}\left(\frac{100\ \mu\mathrm{s}}{10\ \mu\mathrm{s}}\right) = \mathbf{+10.00\ \mathrm{dB}} \qquad \mathrm{(4)}",
            9.2,
            0.36
        )
    ]

    for fname, eq_text, fsize, height_in in equations:
        fig = plt.figure(figsize=(7.2, height_in), dpi=300)
        fig.patch.set_alpha(0.0)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.patch.set_alpha(0.0)
        ax.text(0.5, 0.5, f"${eq_text}$", fontsize=fsize, ha='center', va='center', color='#002B49')
        out_path = eq_dir / fname
        plt.savefig(str(out_path), dpi=300, bbox_inches='tight', pad_inches=0.03, transparent=True)
        plt.close(fig)
        print(f"Generated {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_equation_images()
