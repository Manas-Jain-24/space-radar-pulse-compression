"""Generate 5-Slide Pitch Deck PDF in 16:9 widescreen format using ReportLab."""

from pathlib import Path
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Widescreen 16:9 dimensions: 11 x 6.1875 inches or 13.333 x 7.5 inches (960 x 540 pt)
PAGE_WIDTH = 960.0
PAGE_HEIGHT = 540.0
PAGE_SIZE = (PAGE_WIDTH, PAGE_HEIGHT)

DARK_BG = colors.HexColor("#0A1224")
CARD_BG = colors.HexColor("#121C34")
CYAN = colors.HexColor("#00D4FF")
GOLD = colors.HexColor("#FFC107")
WHITE = colors.HexColor("#FFFFFF")
GRAY = colors.HexColor("#B4C3D7")
BORDER = colors.HexColor("#23375F")

class SlideDeckCanvas(canvas.Canvas):
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
            self.draw_slide_frame(num_pages)
            super().showPage()
        super().save()

    def draw_slide_frame(self, page_count):
        self.saveState()
        # Slide Background
        self.setFillColor(DARK_BG)
        self.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
        
        # Bottom bar
        self.setStrokeColor(BORDER)
        self.setLineWidth(1)
        self.line(40, 30, PAGE_WIDTH - 40, 30)
        
        self.setFont("Helvetica", 9)
        self.setFillColor(GRAY)
        self.drawString(40, 18, "Utkrishta 2026 | SSG × Research Club, IIIT Sri City — Track 1: Radar Signal Processing (SDSC SHAR)")
        page_str = f"Slide {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - 40, 18, page_str)
        self.restoreState()


def build_pdf_deck(filename="PITCH_DECK.pdf"):
    pdf_path = Path(filename)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=PAGE_SIZE,
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    cat_style = ParagraphStyle(
        'Category',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=CYAN,
        spaceAfter=2
    )
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=WHITE,
        spaceAfter=12
    )
    card_title = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=GOLD,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=WHITE,
        spaceAfter=4
    )
    table_cell = ParagraphStyle(
        'TCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=10,
        textColor=WHITE
    )
    table_cell_bold = ParagraphStyle(
        'TCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.0,
        leading=10,
        textColor=CYAN
    )

    story = []

    # =========================================================================
    # SLIDE 1: TITLE & TEAM
    # =========================================================================
    story.append(Spacer(1, 40))
    s1_cat = Paragraph("UTKRISHTA 2026 | SSG × RESEARCH CLUB, IIIT SRI CITY", ParagraphStyle('S1Cat', parent=cat_style, fontSize=12, alignment=1))
    story.append(s1_cat)
    story.append(Spacer(1, 15))
    
    s1_title = Paragraph("LFM Radar Pulse Compression & +10 dB SNR Boost<br/>for Long-Range Space Target Tracking", ParagraphStyle('S1T', parent=title_style, fontSize=26, leading=32, alignment=1))
    story.append(s1_title)
    story.append(Spacer(1, 10))
    
    s1_sub = Paragraph("Solving the Radar Energy-Resolution Dilemma at 200 km Range with Linear Frequency Modulation", ParagraphStyle('S1Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=GOLD, alignment=1))
    story.append(s1_sub)
    story.append(Spacer(1, 40))
    
    s1_meta = Paragraph("<b>TRACK 1:</b> Radar Signal Processing — Target Detection, Pulse Compression & SNR Enhancement<br/><b>Curated by:</b> Mr. Rajendra Kumar, Scientist, Radar Division, SDSC SHAR<br/><br/><b>Team Name:</b> Team Beyond Signals | <b>Date:</b> October 28–29, 2026", ParagraphStyle('S1Meta', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=16, textColor=GRAY, alignment=1))
    story.append(s1_meta)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: PROBLEM OVERVIEW & RADAR SETUP
    # =========================================================================
    story.append(Paragraph("TRACK 1: RADAR SIGNAL PROCESSING | SDSC SHAR", cat_style))
    story.append(Paragraph("Problem Overview & Space-Tracking System Setup", title_style))
    
    left_p2 = [
        Paragraph("The Long-Range Radar Dilemma", card_title),
        Paragraph("• <b>Mission Goal:</b> Detect distant, small RCS space objects (R = 200 km, RCS = 1.0 m²) for launch tracking at SDSC SHAR.", body_style),
        Paragraph("• <b>Energy vs. Resolution Conflict:</b> Higher range demands higher pulse energy E_t = P_t · τ. For unmodulated rectangular pulses, range resolution is tied to pulse duration: ΔR = c · τ / 2.", body_style),
        Paragraph("• <b>Severe Resolution Degradation:</b> Widening an unmodulated pulse to 100 μs destroys resolution to <b>15.0 km</b> (unusable for orbital tracking).", body_style),
        Paragraph("• <b>The LFM Solution:</b> Modulating carrier frequency across B = 4 MHz achieves <b>ΔR = c/(2B) = 37.5 m</b>, completely invariant to pulse duration!", body_style)
    ]
    right_p2 = [
        Paragraph("SDSC SHAR Radar Link Parameters", ParagraphStyle('CP2', parent=card_title, textColor=CYAN)),
        Paragraph("• <b>Carrier Frequency (f_c):</b> 3.0 GHz (S-Band, λ = 0.1 m)", body_style),
        Paragraph("• <b>Pulse Repetition Time (PRT):</b> 2.0 ms (PRF = 500 Hz, R_unamb = 300 km)", body_style),
        Paragraph("• <b>Chirp Sweep Bandwidth (B):</b> 4.0 MHz (Nominal ΔR = 37.5 m)", body_style),
        Paragraph("• <b>Pulse Widths Compared:</b> 10 μs (TB = 40) vs 100 μs (TB = 400)", body_style),
        Paragraph("• <b>Transmit Peak Power (P_t):</b> 250 kW (53.98 dBW)", body_style),
        Paragraph("• <b>Antenna Gain (G_tx, G_rx):</b> 40.0 dBi each (Beamwidth ~ 1.8°)", body_style),
        Paragraph("• <b>Target Range & RCS:</b> R = 200.0 km, RCS = 1.0 m² (0 dBsm)", body_style),
        Paragraph("• <b>Received Power (P_r):</b> 3.95 × 10⁻¹⁴ W (-134.04 dBW, sub-noise)", body_style),
        Paragraph("• <b>Noise Figure & Losses:</b> F = 2.5 dB, System Loss L = 3.0 dB", body_style)
    ]
    t2 = Table([[left_p2, right_p2]], colWidths=[430, 440])
    t2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), CARD_BG),
        ('BACKGROUND', (1,0), (1,0), CARD_BG),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('BOX', (0,0), (0,0), 1, BORDER),
        ('BOX', (1,0), (1,0), 1, BORDER)
    ]))
    story.append(t2)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: METHODOLOGY & WORKFLOW
    # =========================================================================
    story.append(Paragraph("TRACK 1: RADAR SIGNAL PROCESSING | SDSC SHAR", cat_style))
    story.append(Paragraph("Simulation Methodology & Mathematical Pipeline", title_style))
    
    # Workflow Steps
    w_cells = [
        [Paragraph("<b>Step 1: Signal Synthesis</b><br/>PRT = 2 ms, B = 4 MHz, fs = 16 MHz. Dual LFM up-chirps: s(t) = rect(t/τ) exp(j π kr t²). Slope kr1 = 4e11 Hz/s vs kr2 = 4e10 Hz/s.", table_cell),
         Paragraph("<b>Step 2: Channel & AWGN</b><br/>Radar Range Equation at R = 200 km (delay 1.333 ms). Circular complex AWGN with discrete-time variance Pn = N0 · fs.", table_cell),
         Paragraph("<b>Step 3: Matched Filter (MF)</b><br/>Zero-padded FFT linear cross-correlation: y(t) = ifft(fft(rx) · conj(fft(ref))). Trims circular convolution artifacts.", table_cell),
         Paragraph("<b>Step 4: Detection & CFAR</b><br/>1-D Cell-Averaging CFAR (Nref=48, Nguard=16, Pfa=1e-6). Link margin verification against Swerling 0 Marcum Q model.", table_cell)]
    ]
    tw = Table(w_cells, colWidths=[215, 215, 215, 215])
    tw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, CYAN)
    ]))
    story.append(tw)
    story.append(Spacer(1, 10))

    fig2_path = Path("figures/track1/fig2_lfm_waveforms_and_spectra.png")
    if fig2_path.exists():
        story.append(Image(str(fig2_path), width=750, height=270))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: VISUAL PLOTS & BENCHMARK TABLE
    # =========================================================================
    story.append(Paragraph("TRACK 1: RADAR SIGNAL PROCESSING | SDSC SHAR", cat_style))
    story.append(Paragraph("Quantitative Verification & Experimental Plots", title_style))

    rows4 = [
        [Paragraph("<b>Parameter / Metric</b>", table_cell_bold),
         Paragraph("<b>Pulse 1 (10 μs)</b>", table_cell_bold),
         Paragraph("<b>Pulse 2 (100 μs)</b>", table_cell_bold),
         Paragraph("<b>Gain / Ratio</b>", table_cell_bold)],
        [Paragraph("Time-Bandwidth (TB)", table_cell), Paragraph("40 (16.0 dB)", table_cell), Paragraph("400 (26.0 dB)", table_cell), Paragraph("<b>+10.0 dB</b>", table_cell_bold)],
        [Paragraph("Radiated Energy", table_cell), Paragraph("2.50 J", table_cell), Paragraph("25.00 J", table_cell), Paragraph("<b>+10.0 dB</b>", table_cell_bold)],
        [Paragraph("Theoretical MF SNR", table_cell), Paragraph("17.44 dB", table_cell), Paragraph("27.44 dB", table_cell), Paragraph("<b>+10.00 dB</b>", table_cell_bold)],
        [Paragraph("Simulated Peak SNR", table_cell), Paragraph("17.13 dB", table_cell), Paragraph("27.31 dB", table_cell), Paragraph("<b>+10.18 dB (Valid!)</b>", table_cell_bold)],
        [Paragraph("Nominal Resolution", table_cell), Paragraph("37.50 m", table_cell), Paragraph("37.50 m", table_cell), Paragraph("<b>1.00x (Identical)</b>", table_cell_bold)],
        [Paragraph("Measured -3dB Width", table_cell), Paragraph("35.36 m", table_cell), Paragraph("34.17 m", table_cell), Paragraph("<b>0.97x (Identical)</b>", table_cell_bold)],
        [Paragraph("Required SNR (Pd=0.9)", table_cell), Paragraph("13.18 dB", table_cell), Paragraph("13.18 dB", table_cell), Paragraph("Marcum Q baseline", table_cell)],
        [Paragraph("Theoretical Link Margin", table_cell), Paragraph("+4.25 dB (Marginal)", table_cell), Paragraph("+14.25 dB (Robust)", table_cell), Paragraph("<b>+10.00 dB Boost</b>", table_cell_bold)],
        [Paragraph("CA-CFAR Target Margin", table_cell), Paragraph("+6.81 dB", table_cell), Paragraph("+16.99 dB", table_cell), Paragraph("<b>+10.18 dB Boost</b>", table_cell_bold)]
    ]
    t4 = Table(rows4, colWidths=[150, 95, 95, 105])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#192D50")),
        ('BACKGROUND', (0,1), (-1,-1), CARD_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))

    fig4_path = Path("figures/track1/fig4_pulse_compression_snr_boost.png")
    left_img = Image(str(fig4_path), width=420, height=310) if fig4_path.exists() else Paragraph("Plot missing", body_style)

    main_t4 = Table([[left_img, t4]], colWidths=[430, 445])
    main_t4.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(main_t4)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: INSIGHTS, BONUS EXPERIMENTS & CONCLUSION
    # =========================================================================
    story.append(Paragraph("TRACK 1: RADAR SIGNAL PROCESSING | SDSC SHAR", cat_style))
    story.append(Paragraph("Insights, Bonus Experiments & Conclusions", title_style))

    left_p5 = [
        Paragraph("Operational Insights & Bonus Experiments", card_title),
        Paragraph("• <b>Core Proof Verified:</b> Matched-filter SNR increases by +10.18 dB (theory: +10.00 dB) while range resolution remains invariant at ~35 m for both 10 μs and 100 μs chirps.", body_style),
        Paragraph("• <b>Mission-Critical Link Margin:</b> At 200 km, the 100 μs pulse delivers +14.25 dB link margin and +16.99 dB CFAR margin, preventing target loss during rocket staging.", body_style),
        Paragraph("• <b>Bonus Exp 1 (Multi-Target at 200 km):</b> Two targets separated by 50 m merge into a 15 km blob with unmodulated pulses, but are cleanly separated into 2 distinct peaks with LFM compression.", body_style),
        Paragraph("• <b>Bonus Exp 2 (Mach 5 Doppler Coupling):</b> A 1500 m/s rocket induces -112.5 m range bias. We implemented Chirp Diversity (Up/Down chirp pairs), canceling the bias to -3 m and extracting exact velocity (1500 m/s)!", body_style)
    ]

    fig6_path = Path("figures/track1/fig6_multitarget_resolution.png")
    fig5_path = Path("figures/track1/fig5_detection_and_cfar_margin.png")
    chosen_img = fig6_path if fig6_path.exists() else fig5_path
    right_img5 = Image(str(chosen_img), width=420, height=270) if chosen_img.exists() else Paragraph("Plot missing", body_style)

    t5 = Table([[left_p5, right_img5]], colWidths=[430, 445])
    t5.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,0), CARD_BG),
        ('LEFTPADDING', (0,0), (0,0), 14),
        ('RIGHTPADDING', (0,0), (0,0), 14),
        ('TOPPADDING', (0,0), (0,0), 14),
        ('BOTTOMPADDING', (0,0), (0,0), 14),
        ('BOX', (0,0), (0,0), 1, BORDER)
    ]))
    story.append(t5)

    doc.build(story, canvasmaker=SlideDeckCanvas)
    print(f"Successfully generated 5-Slide Pitch Deck PDF: {pdf_path.resolve()}")

if __name__ == "__main__":
    build_pdf_deck()
