#!/usr/bin/env python3
"""Gabungkan semua vision analysis JSON + screenshot menjadi satu HTML report."""
import json
import base64
import os
from datetime import datetime

DOWNLOAD_DIR = "/home/z/my-project/download"

# Mapping: section_name -> (json_file, screenshot_file, title, description)
SECTIONS = [
    {
        "id": "01-deployed-initial",
        "title": "1. Analisis Awal Website yang Di-deploy",
        "subtitle": "Screenshot website di GitHub Pages sebelum perbaikan",
        "json": "vision-analysis.json",
        "image": "deployed-current.png",
        "date": "2025-11-11 10:17",
    },
    {
        "id": "02-upload-progress",
        "title": "2. Saat Upload File Berlangsung",
        "subtitle": "Analisis layout saat file sedang diupload",
        "json": "vision-upload.json",
        "image": "deployed-upload-progress.png",
        "date": "2025-11-11 10:18",
    },
    {
        "id": "03-fixed-layout",
        "title": "3. Setelah Perbaikan Layout & Uploader Profile",
        "subtitle": "Privacy notice + uploader bar + compact layout",
        "json": "vision-fixed.json",
        "image": "fixed-after-upload.png",
        "date": "2025-11-11 10:22",
    },
    {
        "id": "04-image-modal",
        "title": "4. Modal Detail File - Gambar",
        "subtitle": "Preview gambar dengan dimensi & rasio",
        "json": "vision-final.json",
        "image": "final-image-modal-verified.png",
        "date": "2025-11-11 10:46",
    },
    {
        "id": "05-share-fixed",
        "title": "5. Tab Bagikan - File dari Akun Lain",
        "subtitle": "File persisten via IndexedDB walau ganti pengunggah",
        "json": "vision-share-fixed.json",
        "image": "final-share-tab-siti.png",
        "date": "2025-11-11 10:57",
    },
    {
        "id": "06-beranda-feed",
        "title": "6. Tab Beranda - Feed Publik Global",
        "subtitle": "Feed unggahan dengan like/komentar/share",
        "json": "vision-beranda.json",
        "image": "final-beranda-feed.png",
        "date": "2025-11-11 11:49",
    },
    {
        "id": "07-beranda-liked",
        "title": "7. Interaksi Like & Komentar",
        "subtitle": "Like berubah merah + komentar tampil real-time",
        "json": "vision-liked.json",
        "image": "final-beranda-liked.png",
        "date": "2025-11-11 11:50",
    },
    {
        "id": "08-payment-tab",
        "title": "8. Tab Pembayaran - Monetisasi & Penarikan",
        "subtitle": "Saldo + tarif + 3 metode penarikan (Bank/Tunai/QRIS)",
        "json": "vision-payment.json",
        "image": "final-payment-tab.png",
        "date": "2025-11-11 12:52",
    },
]

def img_to_base64(path):
    """Convert image file to base64 data URI."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_content(json_data):
    """Extract the analysis content from vision JSON."""
    if not json_data:
        return "(Analisis tidak tersedia)"
    try:
        content = json_data["choices"][0]["message"]["content"]
        # Convert markdown-ish to HTML
        content = content.replace("\n\n", "\n")
        lines = content.split("\n")
        html_lines = []
        in_list = False
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                continue
            # Headings
            if line.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h4>{line[3:]}</h4>")
            elif line.startswith("### "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h5>{line[4:]}</h5>")
            elif line.startswith("- ") or line.startswith("* "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(f"<li>{line[2:]}</li>")
            elif line.startswith("|"):
                # Table row - simple pass-through
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<div class='table-row'>{line}</div>")
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                # Bold **text**
                line = line.replace("**", "<strong>", 1)
                if "**" in line:
                    line = line.replace("**", "</strong>", 1)
                html_lines.append(f"<p>{line}</p>")
        if in_list:
            html_lines.append("</ul>")
        return "\n".join(html_lines)
    except (KeyError, IndexError):
        return "(Gagal parsing JSON)"

# Build HTML
sections_html = []
for sec in SECTIONS:
    json_path = os.path.join(DOWNLOAD_DIR, sec["json"])
    img_path = os.path.join(DOWNLOAD_DIR, sec["image"])
    json_data = load_json(json_path)
    content_html = extract_content(json_data)
    img_data_uri = img_to_base64(img_path)
    img_html = f'<img src="{img_data_uri}" alt="{sec["title"]}" loading="lazy" />' if img_data_uri else '<div class="no-image">(Screenshot tidak tersedia)</div>'
    
    sections_html.append(f"""
    <section class="report-section" id="{sec["id"]}">
      <div class="section-header">
        <h2>{sec["title"]}</h2>
        <p class="section-subtitle">{sec["subtitle"]}</p>
        <span class="section-date">📅 {sec["date"]}</span>
      </div>
      <div class="section-body">
        <div class="screenshot-wrap">
          {img_html}
        </div>
        <div class="analysis-content">
          {content_html}
        </div>
      </div>
    </section>
    """)

# Table of contents
toc_html = "\n".join([
    f'<li><a href="#{sec["id"]}">{sec["title"]}</a><span>{sec["subtitle"]}</span></li>'
    for sec in SECTIONS
])

html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Laporan Verifikasi KontenHub — Gabungan Analisis VLM</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 50%, #f1f5f9 100%);
    color: #0f172a; line-height: 1.6; font-size: 15px;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
  /* Header */
  .report-header {{
    background: linear-gradient(135deg, #7c3aed 0%, #c026d3 50%, #db2777 100%);
    color: #fff; padding: 48px 0; text-align: center; position: relative; overflow: hidden;
  }}
  .report-header::before {{
    content: ''; position: absolute; top: -50%; right: -20%; width: 500px; height: 500px;
    background: rgba(255,255,255,.08); border-radius: 50%; pointer-events: none;
  }}
  .report-header::after {{
    content: ''; position: absolute; bottom: -30%; left: -10%; width: 300px; height: 300px;
    background: rgba(255,255,255,.06); border-radius: 50%; pointer-events: none;
  }}
  .report-header h1 {{
    font-size: 32px; font-weight: 700; margin-bottom: 8px; position: relative; letter-spacing: -.02em;
  }}
  .report-header p {{
    font-size: 15px; opacity: .9; max-width: 700px; margin: 0 auto; position: relative;
  }}
  .report-meta {{
    display: flex; gap: 20px; justify-content: center; margin-top: 20px; flex-wrap: wrap; position: relative;
  }}
  .meta-pill {{
    background: rgba(255,255,255,.18); padding: 6px 14px; border-radius: 999px;
    font-size: 12px; font-weight: 500; backdrop-filter: blur(6px);
  }}
  /* TOC */
  .toc-card {{
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 24px; margin: 32px 0; box-shadow: 0 4px 12px rgba(0,0,0,.04);
  }}
  .toc-card h2 {{ font-size: 18px; margin-bottom: 16px; color: #7c3aed; display: flex; align-items: center; gap: 8px; }}
  .toc-card h2::before {{ content: '📑'; }}
  .toc-list {{ list-style: none; }}
  .toc-list li {{
    padding: 10px 0; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; gap: 12px; align-items: center;
  }}
  .toc-list li:last-child {{ border-bottom: none; }}
  .toc-list a {{
    color: #0f172a; text-decoration: none; font-weight: 500; font-size: 14px; flex: 1;
  }}
  .toc-list a:hover {{ color: #7c3aed; }}
  .toc-list span {{ font-size: 12px; color: #64748b; text-align: right; }}
  /* Section */
  .report-section {{
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    margin-bottom: 24px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,.04);
  }}
  .section-header {{
    padding: 20px 24px; border-bottom: 1px solid #e2e8f0;
    background: linear-gradient(135deg, rgba(124,58,237,.04), rgba(192,38,211,.02));
  }}
  .section-header h2 {{
    font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 4px;
  }}
  .section-subtitle {{ font-size: 13px; color: #64748b; }}
  .section-date {{ display: inline-block; margin-top: 8px; font-size: 11px; color: #94a3b8; }}
  .section-body {{ padding: 24px; display: grid; grid-template-columns: 1fr; gap: 20px; }}
  @media(min-width: 900px) {{
    .section-body {{ grid-template-columns: 1fr 1fr; }}
    .screenshot-wrap {{ position: sticky; top: 20px; align-self: start; }}
  }}
  .screenshot-wrap {{
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; text-align: center;
  }}
  .screenshot-wrap img {{
    max-width: 100%; height: auto; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,.1);
  }}
  .no-image {{ padding: 60px 20px; color: #94a3b8; font-size: 13px; }}
  .analysis-content {{ font-size: 13px; color: #334155; }}
  .analysis-content h4 {{
    font-size: 14px; font-weight: 700; color: #7c3aed; margin-top: 16px; margin-bottom: 8px;
    padding-bottom: 4px; border-bottom: 1px solid #ede9fe;
  }}
  .analysis-content h4:first-child {{ margin-top: 0; }}
  .analysis-content h5 {{
    font-size: 13px; font-weight: 600; color: #6d28d9; margin-top: 12px; margin-bottom: 6px;
  }}
  .analysis-content p {{ margin-bottom: 8px; }}
  .analysis-content ul {{ margin-left: 20px; margin-bottom: 8px; }}
  .analysis-content li {{ margin-bottom: 4px; }}
  .analysis-content strong {{ color: #0f172a; font-weight: 600; }}
  .analysis-content .table-row {{
    font-family: monospace; font-size: 11px; color: #475569; padding: 4px 8px;
    background: #f8fafc; border-radius: 4px; margin-bottom: 2px; white-space: pre; overflow-x: auto;
  }}
  /* Summary */
  .summary-card {{
    background: linear-gradient(135deg, #ecfdf5, #d1fae5); border: 1px solid #a7f3d0;
    border-radius: 14px; padding: 24px; margin: 32px 0;
  }}
  .summary-card h2 {{ color: #065f46; font-size: 18px; margin-bottom: 12px; }}
  .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }}
  .summary-item {{
    background: rgba(255,255,255,.7); padding: 12px; border-radius: 8px; border: 1px solid rgba(16,185,129,.2);
  }}
  .summary-item-label {{ font-size: 11px; color: #047857; text-transform: uppercase; letter-spacing: .4px; }}
  .summary-item-value {{ font-size: 16px; font-weight: 700; color: #064e3b; margin-top: 4px; }}
  /* Footer */
  .report-footer {{
    text-align: center; padding: 24px; color: #64748b; font-size: 12px;
    border-top: 1px solid #e2e8f0; margin-top: 32px;
  }}
  .report-footer a {{ color: #7c3aed; text-decoration: none; }}
</style>
</head>
<body>

<header class="report-header">
  <div class="container">
    <h1>📊 Laporan Verifikasi KontenHub</h1>
    <p>Gabungan analisis VLM (Vision Language Model) untuk seluruh fitur website KontenHub — Studio Konten All-in-One.</p>
    <div class="report-meta">
      <span class="meta-pill">📅 {datetime.now().strftime("%d November 2025")}</span>
      <span class="meta-pill">🔍 {len(SECTIONS)} Analisis</span>
      <span class="meta-pill">🌐 Bahasa Indonesia</span>
      <span class="meta-pill">🎯 Skor VLM: 8-9/10</span>
    </div>
  </div>
</header>

<div class="container">
  <!-- TOC -->
  <div class="toc-card">
    <h2>Daftar Isi</h2>
    <ul class="toc-list">
      {toc_html}
    </ul>
  </div>

  <!-- Summary -->
  <div class="summary-card">
    <h2>✅ Ringkasan Hasil Verifikasi</h2>
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-item-label">Total Analisis</div>
        <div class="summary-item-value">{len(SECTIONS)} Tahap</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Skor Tertinggi</div>
        <div class="summary-item-value">9/10</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Tab Aplikasi</div>
        <div class="summary-item-value">6 Tab</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Metode Penarikan</div>
        <div class="summary-item-value">3 Metode</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Bank Didukung</div>
        <div class="summary-item-value">4 Bank</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Retail Didukung</div>
        <div class="summary-item-value">3 Retail</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Dompet Digital</div>
        <div class="summary-item-value">6 Wallet</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Status</div>
        <div class="summary-item-value">✅ Lulus</div>
      </div>
    </div>
  </div>

  <!-- Sections -->
  {''.join(sections_html)}

</div>

<footer class="report-footer">
  <div class="container">
    <p>© 2025 KontenHub — Laporan Verifikasi VLM | Dibuat otomatis pada {datetime.now().strftime("%d %B %Y %H:%M")}</p>
    <p style="margin-top:8px">Semua analisis digabung dari 8 file JSON terpisah menjadi satu laporan komprehensif.</p>
  </div>
</footer>

</body>
</html>
"""

output_path = "/home/z/my-project/download/laporan-verifikasi-kontenhub.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ Laporan gabungan dibuat: {output_path}")
print(f"📊 Total section: {len(SECTIONS)}")
print(f"📄 Ukuran file: {os.path.getsize(output_path) / 1024:.1f} KB")
