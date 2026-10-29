"""
Final Submission Bundle Packager
================================
Beyond the Signal: Radar Systems & Applied Space-Tech 24-Hour Research-Athon (Utkrishta 2026)
Track 1: Radar Signal Processing (Curated by Mr. Rajendra Kumar, Scientist, SDSC SHAR, ISRO)

Packages all required submission deliverables into a clean, standalone ZIP archive:
  - 2-Page IEEE Camera-Ready Technical Note (PDF)
  - 5-Slide Finalist Pitch Deck (PDF & PPTX)
  - Full Presentation Script & Jury Defense Q&A (Markdown)
  - Interactive Web Dashboard (Zero-install HTML5 GUI)
  - Interactive Google Colab Notebook (Jupyter .ipynb)
  - Core Python Simulation & All 8 Bonus / Advanced Upgrades
  - All 13 Publication Figures (300 DPI PNGs)
"""

import os
import zipfile
from report_data import atomic_output

def create_submission_bundle():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    zip_filename = os.path.join(base_dir, "submission_bundle.zip")
    
    files_to_include = [
        # Primary Deliverables
        "TECHNICAL_NOTE_IEEE.pdf",
        "PITCH_DECK.pdf",
        "PITCH_DECK.pptx",
        "PITCH_DECK.md",
        "TECHNICAL_NOTE.md",
        "README.md",
        "requirements.txt",
        "dashboard.html",
        "index.html",
        
        # Core & Bonus Code
        "track1_lfm_simulation.py",
        "radar_metrics.py",
        "artifact_io.py",
        "figures/track1/simulation_results.json",
        "tests/stress_test_suite.py",
        "tests/test_regressions.py",
        "scripts/report_data.py",
        "scripts/update_written_results.py",
        "track1_bonus_upgrades.py",
        "track1_radar_notebook.ipynb",
        "app.py",
        
        # Advanced Engineering Suite
        "advanced_upgrade1_ambiguity.py",
        "advanced_upgrade2_cfar_family.py",
        "advanced_upgrade3_coherent_range_doppler.py",
        "advanced_upgrade4_nlfm_waveform.py",
        "advanced_upgrade5_hardware_imperfections.py",
        
        # Generation Scripts
        "scripts/generate_pdf_report.py",
        "scripts/generate_pitch_deck.py",
        "scripts/generate_pitch_deck_pdf.py",
        "scripts/generate_equation_images.py",
        "scripts/package_submission.py",
    ]
    
    # Add all 13 figures
    figures_dir = os.path.join(base_dir, "figures", "track1")
    if os.path.exists(figures_dir):
        for fig_name in sorted(os.listdir(figures_dir)):
            if fig_name.endswith(".png"):
                files_to_include.append(os.path.join("figures", "track1", fig_name).replace("\\", "/"))
        equations_dir = os.path.join(figures_dir, "equations")
        if os.path.exists(equations_dir):
            for fig_name in sorted(os.listdir(equations_dir)):
                if fig_name.endswith(".png"):
                    files_to_include.append(os.path.join("figures", "track1", "equations", fig_name).replace("\\", "/"))
                
    print("=" * 75)
    print("PACKAGING UTKRISHTA 2026 TRACK 1 SUBMISSION BUNDLE")
    print("=" * 75)
    
    total_uncompressed_bytes = 0
    included_count = 0
    
    with atomic_output(zip_filename) as temporary, zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for rel_path in files_to_include:
            full_path = os.path.join(base_dir, rel_path)
            if os.path.exists(full_path):
                size_bytes = os.path.getsize(full_path)
                total_uncompressed_bytes += size_bytes
                zipf.write(full_path, arcname=rel_path)
                print(f"  [+] Added: {rel_path:<45} ({size_bytes / 1024:.1f} KB)")
                included_count += 1
            else:
                raise FileNotFoundError(f"Required submission file missing: {rel_path}")
                
    zip_size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    print("=" * 75)
    print(f"SUCCESS: Created {os.path.basename(zip_filename)}")
    print(f"  Total Files Included  : {included_count}")
    print(f"  Uncompressed Payload  : {total_uncompressed_bytes / (1024 * 1024):.2f} MB")
    print(f"  Final ZIP Bundle Size : {zip_size_mb:.2f} MB")
    print(f"  Bundle File Path      : {zip_filename}")
    print("=" * 75)

if __name__ == "__main__":
    create_submission_bundle()
