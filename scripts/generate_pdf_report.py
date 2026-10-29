"""Generate 2-Page IEEE formatted Technical Note PDF using ReportLab with publication-grade mathematics."""

import os
from pathlib import Path
from report_data import result_text, atomic_output
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def ensure_equation_images():
    """Render crisp, publication-grade LaTeX math equations if not already present."""
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
        out_path = eq_dir / fname
        if not out_path.exists():
            fig = plt.figure(figsize=(7.2, height_in), dpi=300)
            fig.patch.set_alpha(0.0)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')
            ax.patch.set_alpha(0.0)
            ax.text(0.5, 0.5, f"${eq_text}$", fontsize=fsize, ha='center', va='center', color='#002B49')
            plt.savefig(str(out_path), dpi=300, bbox_inches='tight', pad_inches=0.03, transparent=True)
            plt.close(fig)


def register_fonts():
    """Register TrueType Unicode fonts from Windows to prevent missing glyphs."""
    windows_fonts = {
        'Times-Roman': 'C:/Windows/Fonts/times.ttf',
        'Times-Bold': 'C:/Windows/Fonts/timesbd.ttf',
        'Times-Italic': 'C:/Windows/Fonts/timesi.ttf',
        'Helvetica': 'C:/Windows/Fonts/arial.ttf',
        'Helvetica-Bold': 'C:/Windows/Fonts/arialbd.ttf',
        'Courier': 'C:/Windows/Fonts/consola.ttf',
        'Courier-Bold': 'C:/Windows/Fonts/consolab.ttf',
    }
    for font_name, font_path in windows_fonts.items():
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            except Exception:
                pass


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#444444"))
        
        # Header (Top)
        header_text = "Beyond the Signal: Research-Athon (Utkrishta 2026) — Track 1: Radar Signal Processing"
        self.drawString(36, 756, header_text)
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(36, 750, 576, 750)
        
        # Footer (Bottom)
        self.line(36, 42, 576, 42)
        footer_text = "IEEE Technical Note | Track 1 | SSG × Research Club, IIIT Sri City"
        self.drawString(36, 30, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()


def build_pdf(filename="TECHNICAL_NOTE_IEEE.pdf"):
    ensure_equation_images()
    register_fonts()

    pdf_path = Path(filename)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        alignment=1,
        textColor=colors.HexColor('#002B49')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor('#222222')
    )
    
    sec_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.0,
        leading=13,
        textColor=colors.HexColor('#002B49'),
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Times-Roman',
        fontSize=8.7,
        leading=11.1,
        alignment=4,
        spaceAfter=2
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#002B49')
    )

    story = []

    # Title & Metadata
    title_text = "LFM Pulse Compression for a 200 km Radar Target"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 1))
    
    meta_text = "<b>Team Spaceship:</b> Manas Vinod Jain, Vikhyat Gupta<br/><b>Track 1:</b> Radar Signal Processing | <b>Curator:</b> Mr. Rajendra Kumar (Scientist, Radar Division, SDSC SHAR)<br/><b>Organization:</b> SSG × Research Club, IIIT Sri City (Utkrishta 2026)"
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#002B49'), spaceAfter=4))

    abstract = (
        "<b>RESULT IN BRIEF.</b> At fixed peak power, the 100 μs LFM pulse delivers "
        "<b>+{{BOOST}} dB measured matched-filter SNR gain</b> over the 10 μs pulse, while "
        "both retain <b>37.5 m nominal range resolution</b>. A 200-trial production-chain study "
        "finds +{{MC_MEAN}} dB mean gain (95% confidence interval for the mean: {{MC_LOW}}–{{MC_HIGH}} dB)."
    )
    abstract_box = Table([[Paragraph(result_text(abstract), body_style)]], colWidths=[530])
    abstract_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FA')),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#B8D5E4')),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(abstract_box)

    # SECTION 1
    story.append(Paragraph("I. PROBLEM STATEMENT & MATHEMATICAL FORMULATION", sec_heading))
    sec1_a = (
        "<b>A. Radar Energy vs. Resolution Conflict:</b> The Track 1 synthetic target has range <i>R</i> = 200 km and "
        "RCS <i>σ</i> = 1.0 m<sup>2</sup>. Detecting its weak echo requires sufficient radiated pulse energy "
        "<i>E<sub>t</sub></i> = <i>P<sub>t</sub></i> · <i>τ<sub>p</sub></i>. For unmodulated rectangular pulses, range resolution is constrained by pulse duration: "
        "Δ<i>R</i><sub>unmod</sub> = <i>c</i> · <i>τ<sub>p</sub></i> / 2. Widening an unmodulated pulse from 10 μs to 100 μs scales energy by +10 dB "
        "but degrades nominal range resolution from 1.5 km to 15.0 km. Applying Linear Frequency Modulation (LFM) "
        "decouples resolution from pulse width:"
    )
    story.append(Paragraph(sec1_a, body_style))

    # Display Equation (1)
    eq1_path = Path("figures/track1/equations/eq1_resolution.png")
    if eq1_path.exists():
        story.append(Image(str(eq1_path), width=510, height=25.5))

    sec1_b = (
        "<b>B. LFM Chirp & Matched Filter Pulse Compression:</b> A linear chirp sweeps frequency over sweep bandwidth <i>B</i> = 4.0 MHz within duration <i>τ<sub>p</sub></i> "
        "with chirp slope <i>k<sub>r</sub></i> = <i>B</i> / <i>τ<sub>p</sub></i>. The receiver matched filter <i>h</i>(<i>t</i>) = <i>s</i>*(-<i>t</i>) compresses the echo "
        "into a narrow mainlobe. Its nominal range resolution is set primarily by bandwidth <i>B</i>:"
    )
    story.append(Paragraph(sec1_b, body_style))

    # Display Equation (2)
    eq2_path = Path("figures/track1/equations/eq2_waveform.png")
    if eq2_path.exists():
        story.append(Image(str(eq2_path), width=510, height=25.5))

    sec1_c = (
        "<b>C. Illustrative S-Band Link Budget:</b> We assume <i>P<sub>t</sub></i> = 250 kW, <i>G</i> = 40 dBi per antenna, "
        "<i>λ</i> = 0.1 m [3.0 GHz], <i>L</i> = 3.0 dB, and <i>F</i> = 2.5 dB. These are simulation inputs, not published facility specifications. "
        "At <i>R</i> = 200 km, the Radar Range Equation yields:"
    )
    story.append(Paragraph(sec1_c, body_style))

    # Display Equation (3)
    eq3_path = Path("figures/track1/equations/eq3_link_budget.png")
    if eq3_path.exists():
        story.append(Image(str(eq3_path), width=510, height=25.5))

    sec1_d = (
        "Receiver noise spectral density is <i>N</i><sub>0</sub> = <i>k</i><sub>B</sub> <i>T</i><sub>0</sub> <i>F</i> = -201.48 dBW/Hz (7.120 × 10<sup>-21</sup> W/Hz). "
        "Matched filter peak output SNR integrates total received energy <i>E<sub>r</sub></i> = <i>P<sub>r</sub></i> · <i>τ<sub>p</sub></i>. "
        "Comparing <i>τ</i><sub>2</sub> = 100 μs against <i>τ</i><sub>1</sub> = 10 μs proves the fundamental +10 dB SNR scaling law:"
    )
    story.append(Paragraph(sec1_d, body_style))

    # Display Equation (4)
    eq4_path = Path("figures/track1/equations/eq4_snr_scaling.png")
    if eq4_path.exists():
        story.append(Image(str(eq4_path), width=510, height=25.5))

    # SECTION 2
    story.append(Paragraph("II. PROPOSED METHODOLOGY & RADAR PROCESSING PIPELINE", sec_heading))
    sec2_text = (
        "The simulation executes a discrete-time processing chain: (1) Dual LFM chirp generation (<i>B</i> = 4 MHz, <i>τ</i><sub>1</sub> = 10 μs, <i>τ</i><sub>2</sub> = 100 μs) "
        "at <i>f<sub>s</sub></i> = 16 MHz; (2) Pulse train synthesis at PRT = 2.0 ms (PRF = 500 Hz, <i>R</i><sub>unamb</sub> = 300 km); "
        "(3) Target propagation channel at <i>R</i> = 200 km (round-trip delay <i>τ<sub>d</sub></i> = 1.333 ms) with complex circular AWGN; "
        "(4) Zero-padded FFT cross-correlation matched filtering preventing circular wraparound; "
        "(5) 1-D CA-CFAR detection (24 reference and 8 guard cells on each side, <i>P</i><sub>fa</sub> = 10<sup>-6</sup>). "
        "The same peak power, target, and channel assumptions are used in both runs."
    )
    story.append(Paragraph(sec2_text, body_style))

    # Compact, reproducible vector pipeline diagram for the required methodology section.
    pipeline_style = ParagraphStyle(
        'PipelineStep', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=7.0, leading=9.0, alignment=1,
        textColor=colors.HexColor('#002B49')
    )
    arrow_style = ParagraphStyle(
        'PipelineArrow', parent=pipeline_style, fontSize=12,
        textColor=colors.HexColor('#087CA3')
    )
    steps = [
        'Pulse train + LFM<br/><font name="Helvetica" size="6">2 ms PRT; 10/100 μs; 4 MHz</font>',
        'Target + AWGN<br/><font name="Helvetica" size="6">200 km; 1 m²; 1.333 ms</font>',
        'Matched filter<br/><font name="Helvetica" size="6">FFT correlation</font>',
        'Measure<br/><font name="Helvetica" size="6">SNR + mainlobe width</font>',
        'Detect<br/><font name="Helvetica" size="6">CA-CFAR + link margin</font>',
    ]
    pipeline_cells = []
    pipeline_widths = []
    for index, step in enumerate(steps):
        if index:
            pipeline_cells.append(Paragraph('&#8594;', arrow_style))
            pipeline_widths.append(12)
        pipeline_cells.append(Paragraph(step, pipeline_style))
        pipeline_widths.append(92)
    pipeline = Table([pipeline_cells], colWidths=pipeline_widths)
    pipeline.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FA')),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#A8C4D4')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(Spacer(1, 5))
    story.append(pipeline)
    story.append(Paragraph("<b>Fig. 1:</b> End-to-end Track 1 simulation pipeline.", ParagraphStyle('PipelineCaption', parent=styles['Normal'], fontSize=6.5, alignment=1, textColor=colors.HexColor('#444444'))))

    # Embed Figure 1: Waveforms & Spectra
    fig2_path = Path("figures/track1/fig2_lfm_waveforms_and_spectra.png")
    if fig2_path.exists():
        story.append(Spacer(1, 2))
        story.append(Image(str(fig2_path), width=510, height=155))
        story.append(Paragraph("<b>Fig. 2:</b> Synthesized LFM chirp time-domain waveforms and normalized frequency spectra (<i>B</i> = 4.0 MHz) for 10 μs and 100 μs pulses.", ParagraphStyle('Cap', parent=styles['Normal'], fontSize=6.5, alignment=1, textColor=colors.HexColor('#444444'))))

    story.append(PageBreak()) # EXACTLY ADVANCE TO PAGE 2

    # PAGE 2: RESULTS & TAKEAWAYS
    story.append(Paragraph("III. QUANTITATIVE RESULTS, BENCHMARK COMPARISON & VALIDATION", sec_heading))

    # Results Table
    table_data = [
        [Paragraph("<b>Radar System Metric / Parameter</b>", table_cell_bold),
         Paragraph("<b>Pulse 1 (<i>τ</i><sub>1</sub> = 10 μs)</b>", table_cell_bold),
         Paragraph("<b>Pulse 2 (<i>τ</i><sub>2</sub> = 100 μs)</b>", table_cell_bold),
         Paragraph("<b>Enhancement / Comparison</b>", table_cell_bold)],
        [Paragraph("Radiated Pulse Energy (<i>P<sub>t</sub></i> = 250 kW)", table_cell), Paragraph("2.50 J", table_cell), Paragraph("25.00 J", table_cell), Paragraph("+10.0 dB", table_cell)],
        [Paragraph("Theoretical Matched-Filter SNR", table_cell), Paragraph(result_text("{{THEORY1}} dB"), table_cell), Paragraph(result_text("{{THEORY2}} dB"), table_cell), Paragraph("<b>+10.00 dB predicted</b>", table_cell)],
        [Paragraph("Measured Peak SNR", table_cell), Paragraph(result_text("{{SNR1}} dB"), table_cell), Paragraph(result_text("{{SNR2}} dB"), table_cell), Paragraph(result_text("<b>+{{BOOST}} dB observed</b>"), table_cell)],
        [Paragraph("Nominal Range Resolution <i>c</i> / (2<i>B</i>)", table_cell), Paragraph("37.50 m", table_cell), Paragraph("37.50 m", table_cell), Paragraph("Same 4 MHz bandwidth", table_cell)],
        [Paragraph("Measured Half-Power (-3 dB) Width", table_cell), Paragraph(result_text("{{WIDTH1}} m"), table_cell), Paragraph(result_text("{{WIDTH2}} m"), table_cell), Paragraph("Similar compressed peaks", table_cell)],
        [Paragraph("Theoretical Link Margin", table_cell), Paragraph(result_text("+{{MARGIN1}} dB"), table_cell), Paragraph(result_text("+{{MARGIN2}} dB"), table_cell), Paragraph("Illustrative link model", table_cell)],
        [Paragraph("CA-CFAR Target Detection Margin", table_cell), Paragraph(result_text("+{{CFAR1}} dB"), table_cell), Paragraph(result_text("+{{CFAR2}} dB"), table_cell), Paragraph("Adaptive threshold", table_cell)]
    ]
    t = Table(table_data, colWidths=[175, 110, 110, 135])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EBF3F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#002B49')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        result_text("<b>Validation:</b> The fixed-seed core run measures +{{BOOST}} dB versus the +10.00 dB "
        "prediction. A separate 200-trial production-chain experiment measures +{{MC_MEAN}} dB "
        "mean gain (95% confidence interval for the mean {{MC_LOW}}–{{MC_HIGH}} dB). "
        "The small single-run offset reflects finite noise and sampling effects."),
        body_style))

    # Embed Figure 2: Pulse compression zoom
    fig4_path = Path("figures/track1/fig4_pulse_compression_snr_boost.png")
    if fig4_path.exists():
        story.append(Image(str(fig4_path), width=510, height=210))
        story.append(Paragraph(result_text("<b>Fig. 3:</b> Matched filter output at <i>R</i> = 200 km demonstrating the +{{BOOST}} dB SNR boost and similar 35 m mainlobe widths."), ParagraphStyle('Cap2', parent=styles['Normal'], fontSize=6.5, alignment=1, textColor=colors.HexColor('#444444'))))

    story.append(Spacer(1, 3))

    # SECTION 4
    story.append(Paragraph("IV. KEY TAKEAWAYS, PRACTICAL CONSIDERATIONS & LIMITATIONS", sec_heading))
    sec4_text = (
        "<b>1. Interpretation:</b> At equal peak power, the 100 μs pulse carries 10× the energy. "
        "Matched filtering converts that energy into about +10 dB output SNR without broadening the "
        "compressed peak. The link and CFAR margins increase under the chosen illustrative parameters.<br/>"
        "<b>2. Minimum Range Blind Zone:</b> Monostatic transmission blinds reception over <i>R</i><sub>min</sub> = <i>c</i> <i>τ<sub>p</sub></i> / 2. "
        "For <i>τ</i> = 100 μs, <i>R</i><sub>min</sub> = 15.0 km (versus 1.5 km for 10 μs). A mixed short/long-pulse schedule is one possible design response.<br/>"
        "<b>3. Doppler Shift Coupling:</b> Target radial velocity <i>v<sub>r</sub></i> induces Doppler frequency <i>f<sub>d</sub></i> = 2<i>v<sub>r</sub></i> / <i>λ</i>, "
        "causing an apparent range bias Δ<i>R</i> = -<i>c f<sub>d</sub></i> / (2 <i>k<sub>r</sub></i>). Transmitting alternating up- and down-chirps "
        "can reduce this bias and estimate target velocity.<br/>"
        "<b>4. Scope:</b> This is an AWGN point-target simulation, not a field measurement. Clutter, "
        "propagation, fluctuating RCS, and receiver imperfections can change detection performance. "
        "Reproduce the core plots with <font name='Courier'>python track1_lfm_simulation.py</font> "
        "and the 200-trial check included in the saved simulation results. The nominal CA-CFAR false-alarm model assumes independent cells, while oversampled filter outputs are correlated."
    )
    story.append(Paragraph(sec4_text, body_style))

    with atomic_output(doc.filename) as temporary:
        doc.filename = str(temporary)
        doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated IEEE Technical Note: {pdf_path.resolve()}")


if __name__ == "__main__":
    build_pdf()
