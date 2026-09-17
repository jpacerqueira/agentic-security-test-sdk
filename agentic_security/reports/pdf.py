"""Combined A4 PDF of every HTML report, executive summary first."""

from __future__ import annotations

from pathlib import Path
import re

from agentic_security.brand import APP_NAME
from agentic_security.plans import reports_for_pdf
from agentic_security.reports.html import GENERATORS, _client, esc

_HEADER = re.compile(r"<header class=\"cover\">.*?</header>", re.DOTALL)
_MAIN = re.compile(r"<main>(.*?)</main>", re.DOTALL)

A4_CSS = """
@page {
  size: A4;
  margin: 12mm 12mm 16mm 12mm;
}
html, body {
  margin: 0;
  padding: 0;
  background: #fff;
  color: #171D1D;
  font-family: "Liberation Sans", "DejaVu Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 9pt;
  line-height: 1.4;
}
.pdf-section {
  page-break-before: always;
  max-width: 186mm;
}
.pdf-section:first-child { page-break-before: auto; }
header.cover {
  padding: 0 0 8mm;
  border-top: 3pt solid #171D1D;
}
.dot {
  width: 8pt; height: 8pt; border-radius: 50%; background: #ED3A12; margin: 6pt 0 10pt;
}
.cls {
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  font-size: 7.5pt; letter-spacing: 0.08em; text-transform: uppercase; color: #91969C;
}
h1, h2, h3 {
  font-family: "Liberation Serif", "DejaVu Serif", Georgia, serif;
  font-weight: 400; letter-spacing: -0.005em; margin: 0 0 0.4em;
  page-break-after: avoid;
}
h1 { font-size: 16pt; }
h2 { font-size: 12pt; margin-top: 10pt; }
h3 { font-size: 10.5pt; margin-top: 8pt; }
table {
  width: 100%;
  max-width: 186mm;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 7.5pt;
}
th, td {
  text-align: left;
  padding: 3pt 4pt;
  border-bottom: 0.4pt solid #D5D5D5;
  vertical-align: top;
  overflow-wrap: anywhere;
  word-break: break-word;
}
th {
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  font-size: 6.5pt;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #91969C;
}
.badge {
  display: inline-block; padding: 1pt 4pt;
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  font-size: 6.5pt; letter-spacing: 0.04em; text-transform: uppercase;
}
.CRITICAL, .HIGH { background: #FDECEA; color: #C0392B; border: 0.4pt solid #F5C6C2; }
.MEDIUM, .fail, .gap, .catalogue { background: #FEF3E2; color: #A0522D; border: 0.4pt solid #F5DFB8; }
.LOW, .INFO, .UNKNOWN, .PASS, .pass, .met, .collected, .in-progress {
  background: #EAF4EA; color: #2E7D32; border: 0.4pt solid #B8DDB8;
}
.statrow { display: flex; flex-wrap: wrap; gap: 6pt; margin: 8pt 0 12pt; }
.stat { background: #E6EAE6; padding: 6pt 8pt; min-width: 0; flex: 1 1 28%; }
.stat b { display: block; font-family: "Liberation Serif", "DejaVu Serif", serif; font-size: 13pt; font-weight: 400; }
.stat span {
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  font-size: 6.5pt; text-transform: uppercase; color: #91969C; letter-spacing: 0.05em;
}
.callout { background: #FEF3E2; border-left: 2.5pt solid #ED3A12; padding: 6pt 8pt; margin: 8pt 0; }
.evidence {
  background: #E6EAE6; padding: 6pt 8pt;
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  font-size: 7pt; white-space: pre-wrap; overflow-wrap: anywhere; margin: 6pt 0 10pt;
}
code {
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  background: #E6EAE6; padding: 0 2pt; font-size: 7.5pt; overflow-wrap: anywhere; word-break: break-all;
}
iframe, img { max-width: 100%; height: auto; }
ul { padding-left: 1.1em; }
.pdf-toc { page-break-after: always; }
.pdf-toc ol { padding-left: 1.4em; }
"""


def _section_from_html(doc: str) -> str:
    header = _HEADER.search(doc)
    main = _MAIN.search(doc)
    parts = []
    if header:
        parts.append(header.group(0))
    if main:
        parts.append(f"<div class='pdf-body'>{main.group(1)}</div>")
    return "\n".join(parts) if parts else doc


def combined_html(run_dir: Path, meta: dict) -> tuple[str, list[str]]:
    """Return (html, filenames) for the output pack. Executive summary is first."""
    wanted = list(reports_for_pdf(meta.get("plan") or "essentials"))
    present = []
    sections = []
    for name in wanted:
        gen = GENERATORS.get(name)
        path = run_dir / "reports" / name
        if gen:
            doc = gen(run_dir, meta)
        elif path.exists():
            doc = path.read_text(encoding="utf-8")
        else:
            continue
        present.append(name)
        sections.append(f'<article class="pdf-section" id="{esc(name)}">{_section_from_html(doc)}</article>')
    toc = "".join(f"<li>{esc(n)}</li>" for n in present)
    who = _client(meta)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(APP_NAME)} — output report</title>
</head>
<body>
<article class="pdf-section pdf-toc">
  <header class="cover">
    <div class="dot"></div>
    <p class="cls">{esc(who)} confidential · {esc(APP_NAME)}</p>
    <h1>Output report</h1>
  </header>
  <p>Bound A4 pack for run <code>{esc(meta.get("run_id"))}</code>
  · client <strong>{esc(who)}</strong>
  · plan <code>{esc(meta.get("plan"))}</code>.</p>
  <h2>Contents (executive summary first)</h2>
  <ol>{toc}</ol>
</article>
{"".join(sections)}
</body>
</html>"""
    return html, present


def write_output_pdf(run_dir: Path, meta: dict, out_path: Path | None = None) -> Path:
    from weasyprint import CSS, HTML

    html, _present = combined_html(run_dir, meta)
    reports_dir = run_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    dest = out_path or (reports_dir / "output-report.pdf")
    HTML(string=html, base_url=str(reports_dir)).write_pdf(
        dest,
        stylesheets=[CSS(string=A4_CSS)],
    )
    return dest
