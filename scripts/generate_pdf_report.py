"""Generate 2-Page IEEE formatted Technical Note PDF using ReportLab."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

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
        footer_text = "IEEE Technical Note | SDSC SHAR & SSG × Research Club, IIIT Sri City"
        self.drawString(36, 30, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()


def build_pdf(filename="TECHNICAL_NOTE_IEEE.pdf"):
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
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        alignment=1, # Center
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
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#002B49'),
        spaceBefore=5,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Times-Roman',
        fontSize=8.0,
        leading=10.2,
        alignment=4, # Justified
        spaceAfter=3
    )

    math_style = ParagraphStyle(
        'Math',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#8B0000'),
        alignment=1,
        spaceBefore=2,
        spaceAfter=3
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.0,
        leading=8.5
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=8.5,
        textColor=colors.HexColor('#002B49')
    )

    story = []

    # Title & Metadata
    title_text = "LFM Pulse Compression, Link Budget Modeling & +10 dB SNR Enhancement for Long-Range Radar Target Detection"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 2))
    
    meta_text = "<b>Track 1:</b> Radar Signal Processing | <b>Curator:</b> Mr. Rajendra Kumar (Scientist, Radar Division, SDSC SHAR)<br/><b>Organization:</b> SSG × Research Club, IIIT Sri City (Utkrishta 2026)"
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#002B49'), spaceAfter=5))

    # SECTION 1
    story.append(Paragraph("I. PROBLEM STATEMENT & MATHEMATICAL FORMULATION", sec_heading))
    sec1_text = (
        "<b>A. Radar Dilemma:</b> In long-range tracking radars (e.g., SDSC SHAR space launch tracking at R = 200 km, RCS = 1.0 m²), "
        "detecting weak echoes demands high pulse energy E_t = P_t · τ_p. For simple unmodulated pulses, range resolution degrades "
        "linearly with pulse duration: ΔR = c · τ_p / 2. Widening an unmodulated pulse from 10 μs to 100 μs scales energy by +10 dB "
        "but severely corrupts resolution from 1.5 km to 15.0 km, destroying target discrimination.<br/>"
        "<b>B. Linear Frequency Modulation (LFM):</b> Pulse compression resolves this dilemma by sweeping carrier frequency over bandwidth B = 4.0 MHz within pulse duration τ_p: s(t) = rect(t/τ_p) exp(j π k_r t²), with chirp slope k_r = B / τ_p. "
        "The matched filter impulse response h(t) = s*(-t) yields compressed autocorrelation y(t) = τ_p · sinc(π B t). "
        "Crucially, the compressed range resolution is governed <i>exclusively</i> by sweep bandwidth B, independent of pulse width τ_p:"
    )
    story.append(Paragraph(sec1_text, body_style))
    story.append(Paragraph("ΔR = c / (2B) = 3.0×10⁸ / (2 × 4.0×10⁶) = 37.50 m  (Identical for τ = 10 μs and τ = 100 μs)", math_style))

    sec1_text2 = (
        "<b>C. Radar Link Budget & +10 dB SNR Scaling:</b> Received target power P_r at R = 200 km (P_t = 250 kW, G = 40 dBi, "
        "λ = 0.1 m [S-band, 3.0 GHz], L = 3.0 dB, F = 2.5 dB) via the Radar Range Equation is P_r = -134.04 dBW (3.946×10⁻¹⁴ W). "
        "Noise spectral density is N₀ = k_B T₀ F = -201.48 dBW/Hz (7.12×10⁻²¹ W/Hz). Matched filter peak output SNR is SNR_MF = 2 E_r / N₀ = P_r τ_p / N₀. "
        "Comparing τ₂ = 100 μs against τ₁ = 10 μs yields the fundamental +10 dB SNR boost:"
    )
    story.append(Paragraph(sec1_text2, body_style))
    story.append(Paragraph("ΔSNR_MF = 10 log₁₀(τ₂ / τ₁) = 10 log₁₀(100 μs / 10 μs) = +10.00 dB  (Time-Bandwidth: 40 vs 400)", math_style))

    # SECTION 2
    story.append(Paragraph("II. PROPOSED METHODOLOGY & RADAR PROCESSING PIPELINE", sec_heading))
    sec2_text = (
        "The complete end-to-end discrete-time radar processing chain executes: (1) Dual LFM chirp generation (B = 4 MHz, τ₁ = 10 μs, τ₂ = 100 μs) at f_s = 16 MHz; "
        "(2) Pulse train synthesis at PRT = 2.0 ms (PRF = 500 Hz, R_unamb = 300 km); (3) Target channel modeling at R = 200 km (delay τ_d = 1.333 ms) with circular complex AWGN; "
        "(4) Zero-padded FFT cross-correlation matched filtering preventing circular wraparound; (5) Adaptive 1-D CA-CFAR detection (48 reference cells, 16 guard cells, P_fa = 10⁻⁶)."
    )
    story.append(Paragraph(sec2_text, body_style))

    # Embed Figure 2: Waveforms & Spectra
    fig2_path = Path("figures/track1/fig2_lfm_waveforms_and_spectra.png")
    if fig2_path.exists():
        story.append(Image(str(fig2_path), width=530, height=170))
        story.append(Paragraph("<b>Fig. 1:</b> LFM chirp time-domain waveforms and normalized frequency spectra (B = 4.0 MHz) for 10 μs and 100 μs pulses.", ParagraphStyle('Cap', parent=styles['Normal'], fontSize=6.5, alignment=1, textColor=colors.HexColor('#444444'))))

    story.append(PageBreak()) # FORCE PAGE 2

    # PAGE 2: RESULTS & TAKEAWAYS
    story.append(Paragraph("III. QUANTITATIVE RESULTS, BENCHMARK COMPARISON & VALIDATION", sec_heading))

    # Results Table
    table_data = [
        [Paragraph("<b>Radar System Metric / Parameter</b>", table_cell_bold),
         Paragraph("<b>Pulse 1 (τ₁ = 10 μs)</b>", table_cell_bold),
         Paragraph("<b>Pulse 2 (τ₂ = 100 μs)</b>", table_cell_bold),
         Paragraph("<b>Enhancement / Comparison</b>", table_cell_bold)],
        [Paragraph("Pulse Duration (τ_p)", table_cell), Paragraph("10.0 μs", table_cell), Paragraph("100.0 μs", table_cell), Paragraph("×10.0 (+10.0 dB)", table_cell)],
        [Paragraph("Duty Cycle (τ_p / PRT, PRT = 2 ms)", table_cell), Paragraph("0.50 %", table_cell), Paragraph("5.00 %", table_cell), Paragraph("×10.0", table_cell)],
        [Paragraph("Radiated Pulse Energy (P_t = 250 kW)", table_cell), Paragraph("2.50 J", table_cell), Paragraph("25.00 J", table_cell), Paragraph("+10.0 dB", table_cell)],
        [Paragraph("Chirp Sweep Slope (k_r = B / τ_p)", table_cell), Paragraph("4.00×10¹¹ Hz/s", table_cell), Paragraph("4.00×10¹⁰ Hz/s", table_cell), Paragraph("1/10 slope", table_cell)],
        [Paragraph("Time-Bandwidth Product (TB = B · τ_p)", table_cell), Paragraph("40.0 (16.02 dB)", table_cell), Paragraph("400.0 (26.02 dB)", table_cell), Paragraph("+10.0 dB compression gain", table_cell)],
        [Paragraph("Theoretical Matched-Filter SNR", table_cell), Paragraph("17.44 dB", table_cell), Paragraph("27.44 dB", table_cell), Paragraph("<b>+10.00 dB exact boost</b>", table_cell)],
        [Paragraph("Simulated Measured Peak SNR", table_cell), Paragraph("17.13 dB", table_cell), Paragraph("27.31 dB", table_cell), Paragraph("<b>+10.18 dB (Validates Theory)</b>", table_cell)],
        [Paragraph("Nominal Range Resolution c/(2B)", table_cell), Paragraph("37.50 m", table_cell), Paragraph("37.50 m", table_cell), Paragraph("<b>Identical Resolution (1.00×)</b>", table_cell)],
        [Paragraph("Measured Half-Power (-3 dB) Width", table_cell), Paragraph("35.36 m", table_cell), Paragraph("34.17 m", table_cell), Paragraph("<b>0.97× (Identical Discrimination)</b>", table_cell)],
        [Paragraph("Peak Sidelobe Level (PSL)", table_cell), Paragraph("-10.49 dB", table_cell), Paragraph("-11.89 dB", table_cell), Paragraph("Matches sampled discrete sinc", table_cell)],
        [Paragraph("Required SNR (P_D = 0.90, P_fa = 10⁻⁶)", table_cell), Paragraph("13.18 dB", table_cell), Paragraph("13.18 dB", table_cell), Paragraph("Marcum Q nonfluctuating model", table_cell)],
        [Paragraph("Theoretical Link Margin", table_cell), Paragraph("+4.25 dB", table_cell), Paragraph("+14.25 dB", table_cell), Paragraph("<b>+10.00 dB Link Margin Boost</b>", table_cell)],
        [Paragraph("CA-CFAR Target Detection Margin", table_cell), Paragraph("+6.81 dB", table_cell), Paragraph("+16.99 dB", table_cell), Paragraph("<b>+10.18 dB above adaptive thresh</b>", table_cell)]
    ]
    t = Table(table_data, colWidths=[175, 110, 110, 135])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EBF3F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#002B49')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t)
    story.append(Spacer(1, 4))

    # Embed Figure 4: Pulse compression zoom
    fig4_path = Path("figures/track1/fig4_pulse_compression_snr_boost.png")
    if fig4_path.exists():
        story.append(Image(str(fig4_path), width=530, height=185))
        story.append(Paragraph("<b>Fig. 2:</b> Matched filter output at R = 200 km demonstrating the +10.18 dB SNR boost and identical 35 m mainlobe resolution.", ParagraphStyle('Cap2', parent=styles['Normal'], fontSize=6.5, alignment=1, textColor=colors.HexColor('#444444'))))

    story.append(Spacer(1, 4))

    # SECTION 4
    story.append(Paragraph("IV. KEY TAKEAWAYS, PRACTICAL CONSIDERATIONS & LIMITATIONS", sec_heading))
    sec4_text = (
        "<b>1. Operational Significance:</b> While a 10 μs pulse yields a marginal link margin (+4.25 dB) vulnerable to rain fade and pointing errors, "
        "the 100 μs pulse provides an ironclad +14.25 dB link margin and +16.99 dB CFAR margin for mission-critical tracking at SDSC SHAR.<br/>"
        "<b>2. Minimum Range Blind Zone:</b> In monostatic radar, transmission blinds reception over R_min = c τ_p / 2. For τ = 100 μs, R_min = 15.0 km "
        "(versus 1.5 km for 10 μs). Operational tracking radars employ dual-pulse waveforms: short pulses for close-range acquisition and long chirps for distant targets.<br/>"
        "<b>3. Doppler Shift Coupling:</b> Radial velocity v_r induces Doppler frequency f_d = 2v_r / λ, causing a peak time shift Δt = -f_d / k_r. "
        "For space targets, alternating up- and down-chirps effectively resolves range-Doppler ambiguity."
    )
    story.append(Paragraph(sec4_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated IEEE Technical Note: {pdf_path.resolve()}")

if __name__ == "__main__":
    build_pdf()
