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
# TikZ, not the label-list generator above. Chapter 7's chunk overlap
# leads with the real sentence (report #38's, from the naive-split
# example earlier in the chapter) at a large, dominant font size -- the
# words shared between neighbouring chunks are bold and gold-highlighted
# directly in that sentence, which is what actually answers "why does
# overlap help" at a glance. The three chunk boxes are secondary: compact
# stacked bars underneath, in a staircase that reads left-to-right as one
# window sliding across the sentence, not three disconnected diagrams.
# Whole words stand in for tiktoken's real sub-word tokens (readability).
#
# Colors use real alpha (`fill opacity=`), not TikZ's `!12` (which bakes
# in an opaque tint mixed with white at generation time). Real alpha lets
# the page's own background show through, so the same fill value looks
# right on both light and dark themes without a separate dark variant --
# unlike the black sentence text below, which still needs the light->dark
# regex swap in render_tex() since it has no such transparency.
CHUNK_OVERLAP_TEX = r"""
\documentclass[tikz,border=4pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{calc, positioning, backgrounds}
\begin{document}
\begin{tikzpicture}[font=\sffamily]
  \definecolor{chunkTeal}{HTML}{2F9E8F}
  \definecolor{chunkBlue}{HTML}{3B6E9E}
  \definecolor{chunkPlum}{HTML}{7D5BA6}
  \definecolor{sharedGold}{HTML}{B8860B}

  % The sentence itself, at \large -- the dominant element on the page.
  % Words 5-6 and 9-10 are bold: they're the ones repeated across a chunk
  % boundary, so bold marks them before the reader even reaches the gold
  % highlight or the chunk bars below.
  \def\gap{3mm}
  \node[font=\large] (w1) {Trips};
  \node[font=\large, right=\gap of w1] (w2) {During};
  \node[font=\large, right=\gap of w2] (w3) {the};
  \node[font=\large, right=\gap of w3] (w4) {slide};
  \node[font=\large\bfseries, right=\gap of w4] (w5) {lost};
  \node[font=\large\bfseries, right=\gap of w5] (w6) {tool};
  \node[font=\large, right=\gap of w6] (w7) {face};
  \node[font=\large, right=\gap of w7] (w8) {and};
  \node[font=\large\bfseries, right=\gap of w8] (w9) {became};
  \node[font=\large\bfseries, right=\gap of w9] (w10) {assembly};
  \node[font=\large, right=\gap of w10] (w11) {became};
  \node[font=\large, right=\gap of w11] (w12) {stuck};

  % Gold highlight behind the shared words, drawn on the background layer
  % so it sits behind the (already-placed) text instead of covering it.
  \begin{pgfonlayer}{background}
    \draw[fill=sharedGold, fill opacity=0.28, draw=none, rounded corners=2pt]
      ($(w5)+(-1.6mm,-1.8mm)$) rectangle ($(w6)+(1.6mm,3.4mm)$);
    \draw[fill=sharedGold, fill opacity=0.28, draw=none, rounded corners=2pt]
      ($(w9)+(-1.6mm,-1.8mm)$) rectangle ($(w10)+(1.6mm,3.4mm)$);
  \end{pgfonlayer}

  % Chunk bars: compact (5mm tall, 1.5mm apart) and staircased left-to-
  % right under the one shared sentence, reading as a sliding window
  % rather than three separate figures.
  \draw[thick, rounded corners=2pt, draw=chunkTeal, fill=chunkTeal, fill opacity=0.12]
    ($(w1)+(-2mm,-8mm)$) rectangle ($(w6)+(2mm,-13mm)$);
  \draw[thick, rounded corners=2pt, draw=chunkBlue, fill=chunkBlue, fill opacity=0.12]
    ($(w5)+(-2mm,-14.5mm)$) rectangle ($(w10)+(2mm,-19.5mm)$);
  \draw[thick, rounded corners=2pt, draw=chunkPlum, fill=chunkPlum, fill opacity=0.12]
    ($(w9)+(-2mm,-21mm)$) rectangle ($(w12)+(2mm,-26mm)$);

  \node[font=\footnotesize, anchor=east, chunkTeal] at ($(w1)+(-3.2mm,-10.5mm)$) {Chunk 1};
  \node[font=\footnotesize, anchor=east, chunkBlue] at ($(w1)+(-3.2mm,-17mm)$) {Chunk 2};
  \node[font=\footnotesize, anchor=east, chunkPlum] at ($(w1)+(-3.2mm,-23.5mm)$) {Chunk 3};

  % One legend line explaining the gold highlight -- not repeated per
  % overlap the way the old brace-and-"overlap"-label version was.
  \node[font=\footnotesize, text=sharedGold!70!black] at ($(w1)+(0mm,-30mm)$) [anchor=west]
    {\textbullet\ gold highlight = words shared between neighbouring chunks};
\end{tikzpicture}
\end{document}
"""

# Chapter 13's daily loop is a branching flowchart, not a straight chain --
# the duplicate check and the quality gate each have an "exit" path (skip /
# reject) that peels off the main column. Order matters here: it follows
# ingest_report() in code/chapter_13/ingest.py exactly (duplicate check
# before extraction, since there's no reason to extract text from a report
# you're about to discard), not the old ASCII figure's extract-then-dedupe
# order, which the code and the surrounding prose both contradicted.
DAILY_LOOP_TEX = r"""
\documentclass[tikz,border=4pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning}
\begin{document}
\begin{tikzpicture}[
  font=\sffamily,
  box/.style={rectangle, rounded corners=2pt, draw, thick, text width=40mm,
    minimum height=9mm, font=\sffamily\small, align=center},
  exitbox/.style={rectangle, rounded corners=2pt, draw=exitColor, thick,
    text width=27mm, minimum height=9mm, font=\sffamily\small,
    align=center, text=exitColor},
  arr/.style={-{Stealth[length=2.2mm]}, thick},
  exitarr/.style={-{Stealth[length=2.2mm]}, thick, exitColor},
  lbl/.style={font=\scriptsize\itshape}
]
\definecolor{exitColor}{HTML}{B8562F}

\node[box] (arrive) {a new report PDF arrives};
\node[box, below=8mm of arrive] (dup) {already indexed?\\{\scriptsize\itshape duplicate check, by filename}};
\node[exitbox, right=12mm of dup] (skip) {yes $\to$ skip};
\node[box, below=8mm of dup] (extract) {extract text\\{\scriptsize\itshape Chapter 1}};
\node[box, below=8mm of extract] (gate) {quality gate\\{\scriptsize\itshape Chapter 6}};
\node[exitbox, right=12mm of gate] (reject) {fail $\to$ reject,\\review queue};
\node[box, below=8mm of gate] (chunk) {page-aware chunk\\{\scriptsize\itshape Chapter 7}};
\node[box, below=8mm of chunk] (embed) {embed\\{\scriptsize\itshape Chapter 4}};
\node[box, below=8mm of embed] (index) {index.add()\\{\scriptsize\itshape Chapter 8}};
\node[box, below=8mm of index] (gap) {re-run the gap check\\{\scriptsize\itshape Chapter 10}};
\node[box, below=8mm of gap] (question) {``no report filed yesterday?''};

\draw[arr] (arrive) -- (dup);
\draw[arr] (dup) -- node[lbl, left] {no} (extract);
\draw[exitarr] (dup) -- (skip);
\draw[arr] (extract) -- (gate);
\draw[arr] (gate) -- node[lbl, left] {pass} (chunk);
\draw[exitarr] (gate) -- (reject);
\draw[arr] (chunk) -- (embed);
\draw[arr] (embed) -- (index);
\draw[arr] (index) -- (gap);
\draw[arr] (gap) -- (question);
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
        render_tex("theory_ch13_dailyloop", DAILY_LOOP_TEX, workdir)
        print("OK: theory_ch13_dailyloop (branching flowchart, 2 exit paths)")
