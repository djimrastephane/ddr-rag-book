"""Generate synthetic Daily Drilling Report (DDR) PDFs for Chapter 1.

Real DDRs are operationally sensitive, so this book uses fully synthetic
reports that look and read like the real thing. Run this script once to
populate datasets/sample_ddrs/ with a handful of example PDFs before
working through Chapter 1.

Usage:
    python code/chapter_01/generate_sample_ddr.py
"""

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "datasets" / "sample_ddrs"

# Each tuple is (report_no, well, date, depth_md_ft, ops_lines)
SAMPLE_REPORTS = [
    (
        15,
        "EXAMPLE-1H",
        "2025-03-12",
        "9,510 ft",
        [
            "0000-0600  DRLG AHEAD FR 9,320' TO 9,510'. ROP AVG 24 FT/HR. NO LOSSES.",
            "0600-1200  CIRC BU. SLM. NO ISSUES OBSD.",
            "1200-2400  DRLG AHEAD FR 9,510' TO 9,780'. ROP AVG 26 FT/HR.",
        ],
    ),
    (
        16,
        "EXAMPLE-1H",
        "2025-03-13",
        "9,780 ft",
        [
            "0000-0430  DRLG AHEAD FR 9,780' TO 9,842'. TORQUE TREND INCREASING.",
            "0430-0600  CIRC & COND MUD PRIOR TO CONN.",
            "0600-2400  DRLG AHEAD FR 9,842' TO 9,905'. ROP AVG 18 FT/HR. ERRATIC TORQUE.",
        ],
    ),
    (
        17,
        "EXAMPLE-1H",
        "2025-03-14",
        "9,842 ft",
        [
            "0600-1130  POOH FR 9,842' TO CHANGE BHA. ERRATIC TORQUE OBSD LAST 3 STDS.",
            "1130-1400  RIH W/ NEW BHA TO 9,700'. NO ISSUES.",
            "1400-2400  DRLG AHEAD 9,700' TO 9,912'. ROP AVG 22 FT/HR.",
        ],
    ),
    (
        18,
        "EXAMPLE-1H",
        "2025-03-15",
        "9,912 ft",
        [
            "0000-0300  DRLG AHEAD FR 9,912' TO 9,960'. SLOWDOWN OBSD.",
            "0300-0700  STK PIPE @ 9,960'. WORKED PIPE, CIRC & PUMPED PILL.",
            "0700-1100  FREED PIPE. POOH TO 9,500' TO ASSESS BHA CONDITION.",
            "1100-2400  RIH TO 9,960'. WOC OVERNIGHT PER MUD ENGINEER RECOMMENDATION.",
        ],
    ),
    (
        22,
        "EXAMPLE-2H",
        "2025-04-02",
        "11,205 ft",
        [
            "0000-0800  DRLG AHEAD FR 11,050' TO 11,205'. NO LOSSES.",
            "0800-1100  LOT PERFORMED AT CSG SHOE. LOT = 14.8 PPG EMW. FIT WITHIN SPEC.",
            "1100-2400  DRLG AHEAD FR 11,205' TO 11,340'. ROP AVG 30 FT/HR.",
        ],
    ),
]


def build_pdf(report_no: int, well: str, date: str, depth: str, ops_lines: list[str], out_path: Path) -> None:
    c = canvas.Canvas(str(out_path), pagesize=LETTER)
    width, height = LETTER
    left = 0.75 * inch
    y = height - 0.75 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(left, y, "DAILY DRILLING REPORT")
    y -= 0.35 * inch

    c.setFont("Helvetica", 10)
    header = f"WELL: {well}     DATE: {date}     REPORT NO: {report_no}     DEPTH: {depth} MD"
    c.drawString(left, y, header)
    y -= 0.3 * inch

    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y, "24-HR OPERATIONS SUMMARY")
    y -= 0.25 * inch

    c.setFont("Courier", 9)
    for line in ops_lines:
        c.drawString(left, y, line)
        y -= 0.22 * inch

    c.showPage()
    c.save()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for report_no, well, date, depth, ops_lines in SAMPLE_REPORTS:
        out_path = OUTPUT_DIR / f"DDR_{report_no:03d}_{well}.pdf"
        build_pdf(report_no, well, date, depth, ops_lines, out_path)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
