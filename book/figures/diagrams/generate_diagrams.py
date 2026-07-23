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
\usepackage[T1]{{fontenc}}
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


def render_label(label) -> str:
    """A label is either a plain string, or a (main, annotation) tuple --
    the annotation renders as a smaller, italic second line, e.g. a
    "(Chapter 4)" note under a step name."""
    if isinstance(label, tuple):
        main, sub = label
        return f"{escape_latex(main)}\\\\{{\\scriptsize\\itshape {escape_latex(sub)}}}"
    return escape_latex(label)


def build_tex(labels: list, width_mm: int) -> str:
    nodes = []
    for i, label in enumerate(labels):
        text = render_label(label)
        if i == 0:
            nodes.append(f"\\node[box] (n{i}) {{{text}}};")
        else:
            nodes.append(f"\\node[box, below=of n{i-1}] (n{i}) {{{text}}};")
    arrows = [f"\\draw[arr] (n{i}) -- (n{i+1});" for i in range(len(labels) - 1)]
    return TEX_TEMPLATE.format(width=width_mm, nodes="\n".join(nodes), arrows="\n".join(arrows))


def render_tex(name: str, tex_source: str, workdir: Path):
    """Compile a standalone TikZ .tex to PDF, then derive the book's usual
    trio: a light SVG (as-is), a dark SVG (black -> light-gray, since every
    diagram here is monochrome lines/text on a transparent background), and
    a native PDF for the LaTeX build (sidesteps needing rsvg-convert on the
    GitHub Actions runner, which the SVG->PDF path would otherwise require).
    """
    tex_path = workdir / f"{name}.tex"
    tex_path.write_text(tex_source)

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
    (FIGURES_DIR / f"{name}.pdf").write_bytes(pdf_path.read_bytes())


def generate(name: str, labels: list[str], width_mm: int, workdir: Path):
    render_tex(name, build_tex(labels, width_mm), workdir)
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
    "pipeline_ch13": (["New Report", "Append, No Rebuild", "Live Index"], 46),
}

# Second category: linear-chain diagrams inside Theory/Implementation
# sections (not the top-of-chapter progress markers above). A few of this
# book's diagrams branch (yes/no splits in chapters 6, 8, 10) -- those
# aren't here yet, since this generator only draws a straight vertical
# chain; they need branch/conditional support added first.
THEORY_DIAGRAMS = {
    "theory_ch01_extract": ([
        "DDR PDF",
        "open with pdfplumber",
        "for each page:",
        ("page.extract_text()", "-> string, or None if unextractable"),
        "join every page's text together",
        "one Python string, ready for Chapter 2",
    ], 55),
    "theory_ch02_expand": ([
        "raw text",
        "for each (abbreviation, expansion) in dictionary:",
        ("build word-boundary pattern", "case-insensitive"),
        "substitute every match with the expansion",
        "expanded text",
    ], 60),
    "theory_ch04_embed": ([
        "text (\"stuck pipe\")",
        ("embedding model", "all-MiniLM-L6-v2"),
        ("vector", "384 numbers"),
        "compare via cosine similarity",
        "nearby vectors = similar meaning",
    ], 55),
    "theory_ch05_pipeline": ([
        "DDR PDF",
        ("Extraction", "Chapter 1 -- pdfplumber"),
        ("Cleaning", "Chapter 2 -- abbreviation expansion"),
        ("Embeddings", "Chapter 4 -- sentence-transformers"),
        ("Retriever", "Chapter 4 -- cosine similarity search"),
        ("LLM", "this chapter -- prompt + generation"),
        "Answer + Citations",
    ], 62),
    "theory_ch09_hybrid": ([
        "Query",
        "scored two ways",
        "BM25 (sparse, exact terms)",
        "Dense (semantic embedding)",
        ("Reciprocal Rank Fusion", "combine by rank, not score"),
        ("Cross-encoder rerank", "top candidates only"),
        "Results",
    ], 55),
    "theory_ch11_evalloop": ([
        ("hand-labeled questions", "question -> expected report"),
        "run each through the retrieval pipeline",
        "record the rank of the expected report",
        "compute recall@k, MRR, NDCG@k",
        "break results down by category and difficulty",
        ("find the weakest category", "-> that's where to improve next"),
    ], 62),
    "theory_ch12_complete": ([
        ("DDR PDF", "scanned or digital"),
        ("OCR quality gate", "Chapter 6"),
        ("Extraction", "Chapter 1"),
        ("Cleaning", "Chapter 2"),
        ("Segment-aware chunking", "Chapter 7"),
        ("Embeddings", "Chapter 4"),
        ("Hybrid index -- BM25 + FAISS", "Chapters 8-9"),
        ("Retriever + Reranker", "Chapter 9"),
        ("LLM + structured facts", "Chapter 5, 10"),
        ("Answer + Citations + Gaps flagged", "Chapter 10"),
    ], 62),
}

# Third category: one-off diagrams whose shape isn't a chain -- hand-built
# TikZ, not the label-list generator above. Chapter 7's chunk overlap is a
# token strip with three overlapping ranges below it, which `build_tex`
# has no way to express (it only stacks boxes vertically with an arrow
# between each).
CHUNK_OVERLAP_TEX = r"""
\documentclass[tikz,border=3pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{calc, decorations.pathreplacing}
\begin{document}
\begin{tikzpicture}[font=\sffamily]
  \def\dx{9mm}
  \foreach \i in {1,...,12} {
    \node[font=\scriptsize] (t\i) at (\i*\dx, 0) {t\the\numexpr\i\relax};
  }

  % Row geometry: row N box spans y=[top_N, bottom_N]; the 8mm gap between
  % rows holds the overlap brace + label for the columns those two chunks share.
  \draw[thick, rounded corners=2pt] ($(t1)+(-4mm,-6mm)$) rectangle ($(t6)+(4mm,-13mm)$);
  \draw[thick, rounded corners=2pt] ($(t5)+(-4mm,-21mm)$) rectangle ($(t10)+(4mm,-28mm)$);
  \draw[thick, rounded corners=2pt] ($(t9)+(-4mm,-36mm)$) rectangle ($(t12)+(4mm,-43mm)$);

  \node[font=\small, anchor=east] at ($(t1)+(-6mm,-9.5mm)$) {Chunk 1};
  \node[font=\small, anchor=east] at ($(t1)+(-6mm,-24.5mm)$) {Chunk 2};
  \node[font=\small, anchor=east] at ($(t1)+(-6mm,-39.5mm)$) {Chunk 3};

  \draw[decorate, decoration={brace, amplitude=3pt, mirror, raise=1pt}]
    ($(t5)+(-4mm,-14mm)$) -- ($(t6)+(4mm,-14mm)$)
    node[midway, font=\tiny, yshift=-5.5mm] {overlap};

  \draw[decorate, decoration={brace, amplitude=3pt, mirror, raise=1pt}]
    ($(t9)+(-4mm,-29mm)$) -- ($(t10)+(4mm,-29mm)$)
    node[midway, font=\tiny, yshift=-5.5mm] {overlap};
\end{tikzpicture}
\end{document}
"""

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for name, (labels, width) in DIAGRAMS.items():
            generate(name, labels, width, workdir)
        for name, (labels, width) in THEORY_DIAGRAMS.items():
            generate(name, labels, width, workdir)
        render_tex("theory_ch07_chunkoverlap", CHUNK_OVERLAP_TEX, workdir)
        print("OK: theory_ch07_chunkoverlap (token strip, 3 overlapping chunks)")
