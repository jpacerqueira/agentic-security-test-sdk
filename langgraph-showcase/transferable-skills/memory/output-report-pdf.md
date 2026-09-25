---
name: output-report-pdf
description: Combined A4 PDF from Generate output report; executive summary first (2026-09-17)
metadata:
  type: project
---

`GET /runs/{run_id}/output-report.pdf` builds one A4 PDF of every plan HTML report except `full-security-report.html` (that file is an iframe pack of the others). Order comes from `plans.reports_for_pdf()` — `executive-summary.html` is always first.

Implementation:

- `agentic_security/reports/pdf.py` — `combined_html()` + WeasyPrint `write_output_pdf()`, `@page { size: A4 }`
- UI: Reports tab button `#btn-output-pdf` in `run.html`, click handler in `dashboard.js`
- Image packages: pango, cairo, gdk-pixbuf, Liberation/DejaVu fonts in the Dockerfile
- Do not bind live iframe HTML into the PDF; regenerate section bodies from `GENERATORS` so each report is full text
