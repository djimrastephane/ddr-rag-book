#!/usr/bin/env python3
"""Generate this book's pipeline-flow diagrams: TikZ -> PDF -> SVG (light + dark).

Usage: run from anywhere with pdflatex and pdftocairo (poppler) on PATH.
    python3 figures/diagrams/generate_diagrams.py

Each entry in DIAGRAMS produces two files in this directory:
  pipeline_chNN_light.svg  (black on transparent -- used in HTML light mode and PDF)
  pipeline_chNN_dark.svg   (light-gray on transparent -- used in HTML dark mode)

Embed both in a chapter with (see templates/chapter_template.qmd):

::: {.content-visible when-format="html"}
::: {.pipeline-diagram}
![](../figures/diagrams/pipeline_chNN_light.svg){.diagram-light width="180"}
![](../figures/diagrams/pipeline_chNN_dark.svg){.diagram-dark width="180"}
:::
:::

::: {.content-visible when-format="pdf"}
![](../figures/diagrams/pipeline_chNN_light.svg){width="180"}
:::

The light/dark toggle CSS lives in custom.scss (.pipeline-diagram rules),
keyed off the same body.quarto-light / body.quarto-dark classes Quarto's
own theme toggle sets -- <img> can't inherit currentColor from the page,
so two static-color variants is the reliable approach, not one adaptive SVG.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

FIGURES_DIR = Path(__file__).parent

TEX_TEMPLATE = r"""\documentclass[tikz,border=2pt]{{standalone}}
\usepackage{{tikz}}
\usetikzlibrary{{arrows.meta, positioning}}
\begin{{document}}
\begin{{tikzpicture}}[
  node distance=8mm,
  box/.style={{
    rectangle, rounded corners=2pt, draw, thick,
    text width={width}mm, minimum height=9mm,
    font=\sffamily\small, align=center
  }},
  arr/.style={{-{{Stealth[length=2.2mm]}}, thick}}
]
{nodes}
{arrows}
\end{{tikzpicture}}
\end{{document}}
"""


def escape_latex(s: str) -> str:
    return (s.replace("\\", "")
             .replace("&", "\\&")
             .replace("%", "\\%")
             .replace("#", "\\#")
             .replace("_", "\\_"))


def build_tex(labels: list[str], width_mm: int) -> str:
    nodes = []
    for i, label in enumerate(labels):
        esc = escape_latex(label)
        if i == 0:
            nodes.append(f"\\node[box] (n{i}) {{{esc}}};")
        else:
            nodes.append(f"\\node[box, below=of n{i-1}] (n{i}) {{{esc}}};")
    arrows = [f"\\draw[arr] (n{i}) -- (n{i+1});" for i in range(len(labels) - 1)]
    return TEX_TEMPLATE.format(width=width_mm, nodes="\n".join(nodes), arrows="\n".join(arrows))


def generate(name: str, labels: list[str], width_mm: int, workdir: Path):
    tex_path = workdir / f"{name}.tex"
    tex_path.write_text(build_tex(labels, width_mm))

    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", str(tex_path)],
                        cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"PDFLATEX FAILED for {name}:\n{r.stdout[-3000:]}")
        sys.exit(1)

    pdf_path = workdir / f"{name}.pdf"
    svg_light = workdir / f"{name}_light.svg"
    r = subprocess.run(["pdftocairo", "-svg", str(pdf_path), str(svg_light)],
                        cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"PDFTOCAIRO FAILED for {name}:\n{r.stdout}\n{r.stderr}")
        sys.exit(1)

    svg_text = svg_light.read_text()
    dark_text = re.sub(r"rgb\(0%, 0%, 0%\)", "rgb(88%, 88%, 88%)", svg_text)

    (FIGURES_DIR / f"{name}_light.svg").write_text(svg_text)
    (FIGURES_DIR / f"{name}_dark.svg").write_text(dark_text)
    # PDF output embeds the .pdf directly (not the SVG) -- Quarto's LaTeX
    # pipeline needs rsvg-convert to rasterize an SVG for PDF, which isn't
    # installed on the GitHub Actions runner. A native PDF image needs no
    # conversion at all, so this sidesteps that dependency entirely.
    (FIGURES_DIR / f"{name}.pdf").write_bytes(pdf_path.read_bytes())
    print(f"OK: {name} ({len(labels)} boxes, width={width_mm}mm)")


DIAGRAMS = {
    "pipeline_ch00": (["Nothing Installed", "A Working Python Workshop"], 50),
    "pipeline_ch01": (["PDF", "Text"], 32),
    "pipeline_ch02": (["Raw Text", "Expanded Text"], 32),
    "pipeline_ch03": (["Text", "Searchable Archive"], 42),
    "pipeline_ch04": (["Searchable Archive", "Search by Meaning"], 42),
    "pipeline_ch05": (["Question", "Retriever", "LLM", "Answer + Citations"], 40),
    "pipeline_ch06": (["Scanned PDF", "Trusted Text"], 34),
    "pipeline_ch07": (["Whole Report", "Retrievable Chunks"], 40),
    "pipeline_ch08": (["10 Documents", "76-Report Archive", "Persistent Index"], 40),
    "pipeline_ch09": (["Keyword Match + Meaning Match", "Fused Ranking", "Reranked Results"], 52),
    "pipeline_ch10": (["Plausible Answer", "Provable Answer"], 38),
    "pipeline_ch11": (["\"It Feels Like It's Working\"", "Measured, Defensible Performance"], 54),
    "pipeline_ch12": (["1 Well, 76 Reports", "Checkable Patterns", "Toward Cross-Well Intelligence"], 50),
}

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for name, (labels, width) in DIAGRAMS.items():
            generate(name, labels, width, workdir)
