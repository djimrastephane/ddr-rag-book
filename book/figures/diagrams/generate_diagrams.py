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

# Chapter 13's daily loop is a branching flowchart grouped into the four
# phases a drilling/completions engineer actually cares about (Incoming
# Report, Document Processing, AI Processing, Monitoring) rather than one
# undifferentiated vertical chain. Labels favor engineering language over
# Python identifiers (e.g. "Add report to searchable index", not
# "index.add()") -- the reader should recognize what the system is doing,
# not which function got called. Step order still follows
# ingest_report() in code/chapter_13/ingest.py exactly: the duplicate
# check runs before extraction, since there's no reason to extract text
# from a report about to be discarded.
#
# Every fill/stroke below is literal black at partial opacity (fill
# opacity=, draw opacity=, text opacity=), never a hardcoded gray hex.
# That's deliberate: render_tex()'s dark-mode pass only knows how to find
# and swap literal rgb(0%, 0%, 0%) to a light gray. Black-at-low-opacity
# survives that swap intact (opacity is a separate SVG attribute), so the
# phase bands and muted header text automatically land on the right side
# of light-vs-dark contrast in both variants without a second color to
# maintain. exitColor (the skip/reject accent) is the one exception,
# carried over unchanged from the previous version of this figure.
DAILY_LOOP_TEX = r"""
\documentclass[tikz,border=6pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, calc, backgrounds, fit}
\begin{document}
\begin{tikzpicture}[
  font=\sffamily,
  box/.style={rectangle, rounded corners=2pt, draw, thick, text width=44mm,
    minimum height=9mm, font=\sffamily\small, align=center},
  exitbox/.style={rectangle, rounded corners=2pt, draw=exitColor, thick,
    text width=28mm, minimum height=9mm, font=\sffamily\small,
    align=center, text=exitColor},
  arr/.style={-{Stealth[length=2.2mm]}, thick},
  exitarr/.style={-{Stealth[length=2.2mm]}, thick, exitColor},
  lbl/.style={font=\scriptsize\itshape},
  phaselabel/.style={font=\scriptsize\sffamily, anchor=north west, align=left}
]
\definecolor{exitColor}{HTML}{B8562F}

% -- Title -----------------------------------------------------------
\node[font=\sffamily\Large\bfseries, align=center] (title)
  {The Complete Daily DDR\\Processing Pipeline};
\node[font=\sffamily\normalsize\itshape, align=center, below=3mm of title] (subtitle)
  {``Every box is a tool you already built.''};
\draw[thin] ($(subtitle.south west)+(0,-1.2mm)$) -- ($(subtitle.south east)+(0,-1.2mm)$);

% -- Phase 1: Incoming Report -----------------------------------------
\node[box, below=13mm of subtitle] (arrive) {A new report PDF arrives};
\node[box, below=8mm of arrive] (dup)
  {Report already processed?\\{\scriptsize\itshape duplicate check, by filename}};
\node[exitbox, right=12mm of dup] (skip) {Already processed\\$\to$ skip};

% -- Phase 2: Document Processing -------------------------------------
\node[box, below=16mm of dup] (extract) {Extract text\\{\scriptsize\itshape Chapter 1}};
\node[box, below=8mm of extract] (gate)
  {Quality gate (OCR check)\\{\scriptsize\itshape Chapter 6}};
\node[exitbox, right=12mm of gate] (reject) {Fails gate $\to$\\reject, review queue};
\node[box, below=8mm of gate] (chunk) {Page-aware chunking\\{\scriptsize\itshape Chapter 7}};

% -- Phase 3: AI Processing --------------------------------------------
\node[box, below=16mm of chunk] (embed)
  {Convert text into\\AI-searchable vectors\\{\scriptsize\itshape (Embeddings) -- Chapter 4}};
\node[box, below=8mm of embed] (index)
  {Add report to\\searchable index\\{\scriptsize\itshape Chapter 8}};

% -- Phase 4: Monitoring ------------------------------------------------
\node[box, below=16mm of index] (gapcheck)
  {Daily archive health check\\{\scriptsize\itshape Chapter 10}};
\node[box, below=8mm of gapcheck] (missing) {Missing daily report?};
\node[box, below=8mm of missing] (alertbox) {Generate alert};

% -- Arrows -------------------------------------------------------------
\draw[arr] (arrive) -- (dup);
\draw[arr] (dup) -- node[lbl, left] {no} (extract);
\draw[exitarr] (dup) -- (skip);
\draw[arr] (extract) -- (gate);
\draw[arr] (gate) -- node[lbl, left] {pass} (chunk);
\draw[exitarr] (gate) -- (reject);
\draw[arr] (chunk) -- (embed);
\draw[arr] (embed) -- (index);
\draw[arr] (index) -- (gapcheck);
\draw[arr] (gapcheck) -- (missing);
\draw[arr] (missing) -- (alertbox);

% -- Icons: small monochrome pictograms, 9mm left of each main box's ----
% west edge. Hand-drawn with plain paths (no icon font/package) so they
% stay vector and print-safe, and so the black-at-opacity dark-mode trick
% above applies to them too where relevant.
\begin{scope}[shift={($(arrive.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,-2mm) rectangle (1.6mm,2mm);
  \draw (-0.9mm,1mm) -- (0.9mm,1mm);
  \draw (-0.9mm,0mm) -- (0.9mm,0mm);
  \draw (-0.9mm,-1mm) -- (0.4mm,-1mm);
\end{scope}
\begin{scope}[shift={($(dup.west)+(-9mm,0)$)}, thick]
  \draw (-1.4mm,0mm) -- (-0.3mm,-1.3mm) -- (1.6mm,1.6mm);
\end{scope}
\begin{scope}[shift={($(extract.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,1.2mm) -- (1.6mm,1.2mm);
  \draw (-1.6mm,0mm) -- (1.6mm,0mm);
  \draw (-1.6mm,-1.2mm) -- (0.7mm,-1.2mm);
\end{scope}
\begin{scope}[shift={($(gate.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,1.6mm) -- (1.6mm,1.6mm) -- (0.4mm,-0.3mm) -- (0.4mm,-1.7mm)
        -- (-0.4mm,-1.7mm) -- (-0.4mm,-0.3mm) -- cycle;
\end{scope}
\begin{scope}[shift={($(chunk.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,0.2mm) rectangle (-0.2mm,1.6mm);
  \draw (0.2mm,0.2mm) rectangle (1.6mm,1.6mm);
  \draw (-1.6mm,-1.6mm) rectangle (-0.2mm,-0.2mm);
  \draw (0.2mm,-1.6mm) rectangle (1.6mm,-0.2mm);
\end{scope}
\begin{scope}[shift={($(embed.west)+(-9mm,0)$)}, thin]
  \draw (-1.4mm,-1mm) -- (1.4mm,-1mm) -- (0mm,1.4mm) -- cycle;
  \fill (-1.4mm,-1mm) circle (0.35mm);
  \fill (1.4mm,-1mm) circle (0.35mm);
  \fill (0mm,1.4mm) circle (0.35mm);
\end{scope}
\begin{scope}[shift={($(index.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,0.9mm) rectangle (1.6mm,1.7mm);
  \draw (-1.6mm,-0.4mm) rectangle (1.6mm,0.4mm);
  \draw (-1.6mm,-1.7mm) rectangle (1.6mm,-0.9mm);
\end{scope}
\begin{scope}[shift={($(gapcheck.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,-1.6mm) rectangle (-0.7mm,-0.4mm);
  \draw (-0.3mm,-1.6mm) rectangle (0.6mm,0.6mm);
  \draw (1mm,-1.6mm) rectangle (1.9mm,1.6mm);
\end{scope}
\begin{scope}[shift={($(missing.west)+(-9mm,0)$)}, thin]
  \draw (0mm,1.7mm) -- (-1.6mm,-1.3mm) -- (1.6mm,-1.3mm) -- cycle;
  \draw[thick] (0mm,0.9mm) -- (0mm,-0.1mm);
  \fill (0mm,-0.7mm) circle (0.25mm);
\end{scope}
\begin{scope}[shift={($(alertbox.west)+(-9mm,0)$)}, thin]
  \draw (-1mm,-1.7mm) -- (-1mm,1.7mm);
  \draw[fill=exitColor, fill opacity=0.25, draw=exitColor]
    (-1mm,1.7mm) -- (1.6mm,0.9mm) -- (-1mm,0.1mm) -- cycle;
\end{scope}

% -- Phase background bands, drawn behind everything else --------------
% Each band is fit around its boxes plus a coordinate placed at that
% box's icon position, so the tint extends far enough left to enclose
% the icon column too, not just the text boxes.
\begin{pgfonlayer}{background}
  \coordinate (ia) at ($(arrive.west)+(-9mm,0)$);
  \coordinate (id) at ($(dup.west)+(-9mm,0)$);
  \coordinate (h1) at ($(arrive.north)+(0,5mm)$);
  \node[fit=(arrive)(dup)(skip)(ia)(id)(h1), inner sep=4mm, rounded corners=3pt,
    fill=black, fill opacity=0.05, draw=black, draw opacity=0.3, thin] (band1) {};
  \node[phaselabel] at ($(band1.north west)+(2mm,-2.5mm)$)
    {{\bfseries 1}~~\textsc{Incoming Report}};

  \coordinate (ie) at ($(extract.west)+(-9mm,0)$);
  \coordinate (ig) at ($(gate.west)+(-9mm,0)$);
  \coordinate (ic) at ($(chunk.west)+(-9mm,0)$);
  \coordinate (h2) at ($(extract.north)+(0,5mm)$);
  \node[fit=(extract)(gate)(reject)(chunk)(ie)(ig)(ic)(h2), inner sep=4mm,
    rounded corners=3pt, fill=black, fill opacity=0.05, draw=black,
    draw opacity=0.3, thin] (band2) {};
  \node[phaselabel] at ($(band2.north west)+(2mm,-2.5mm)$)
    {{\bfseries 2}~~\textsc{Document Processing}};

  \coordinate (iem) at ($(embed.west)+(-9mm,0)$);
  \coordinate (ii) at ($(index.west)+(-9mm,0)$);
  \coordinate (h3) at ($(embed.north)+(0,5mm)$);
  \node[fit=(embed)(index)(iem)(ii)(h3), inner sep=4mm, rounded corners=3pt,
    fill=black, fill opacity=0.05, draw=black, draw opacity=0.3, thin] (band3) {};
  \node[phaselabel] at ($(band3.north west)+(2mm,-2.5mm)$)
    {{\bfseries 3}~~\textsc{AI Processing}};

  \coordinate (igc) at ($(gapcheck.west)+(-9mm,0)$);
  \coordinate (im) at ($(missing.west)+(-9mm,0)$);
  \coordinate (ial) at ($(alertbox.west)+(-9mm,0)$);
  \coordinate (h4) at ($(gapcheck.north)+(0,5mm)$);
  \node[fit=(gapcheck)(missing)(alertbox)(igc)(im)(ial)(h4), inner sep=4mm,
    rounded corners=3pt, fill=black, fill opacity=0.05, draw=black,
    draw opacity=0.3, thin] (band4) {};
  \node[phaselabel] at ($(band4.north west)+(2mm,-2.5mm)$)
    {{\bfseries 4}~~\textsc{Monitoring}};
\end{pgfonlayer}
\end{tikzpicture}
\end{document}
"""

# Chapter 10's routing decision is a single fork, not a sequential
# pipeline -- unlike Chapter 13's daily loop, "yes" and "no" here are two
# equally valid outcomes (compute an exact answer vs. generate a cited
# one), neither an error/exit path. So this gets a symmetric two-column
# branch instead of Chapter 13's phase-band treatment: same box style,
# same hand-drawn icon technique, same title+subtitle convention, same
# black-at-opacity trick for dark-mode safety, but no exitColor (nothing
# here is an exception) and no phase bands (nothing here is a sequence
# of phases). Labels favor engineering language over the raw filename in
# the old ASCII version ("Look up the structured facts table", not
# "query ddr_facts.parquet") the same way Chapter 13's relabeling did.
ROUTING_TEX = r"""
\documentclass[tikz,border=6pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, calc}
\begin{document}
\begin{tikzpicture}[
  font=\sffamily,
  box/.style={rectangle, rounded corners=2pt, draw, thick, text width=42mm,
    minimum height=9mm, font=\sffamily\small, align=center},
  arr/.style={-{Stealth[length=2.2mm]}, thick},
  lbl/.style={font=\scriptsize\itshape}
]

% -- Title -------------------------------------------------------------
\node[font=\sffamily\Large\bfseries, align=center] (title)
  {Routing a Question:\\Compute or Generate?};
\node[font=\sffamily\normalsize\itshape, align=center, text width=90mm,
  below=3mm of title] (subtitle)
  {``If it's in the structured data, compute it -- don't generate it.''};
\draw[thin] ($(subtitle.south west)+(0,-1.2mm)$) -- ($(subtitle.south east)+(0,-1.2mm)$);

% -- Main chain ----------------------------------------------------------
\node[box, below=13mm of subtitle] (q) {A question arrives};
\node[box, below=9mm of q] (decision) {Answerable from\\structured data?};

\node[box, below left=16mm and 4mm of decision] (lookup)
  {Look up the structured\\facts table\\{\scriptsize\ttfamily ddr\_facts.parquet}};
\node[box, below right=16mm and 4mm of decision] (generate)
  {Retrieve relevant passages\\and generate an answer\\{\scriptsize\itshape Chapter 5}};

\node[box, below=8mm of lookup] (exact) {Exact, re-derivable answer};
\node[box, below=8mm of generate] (cited)
  {Answer with citations\\{\scriptsize\itshape verify before trusting}};

% -- Arrows --------------------------------------------------------------
\draw[arr] (q) -- (decision);
\draw[arr] (decision) -- node[lbl, above, sloped] {yes} (lookup);
\draw[arr] (decision) -- node[lbl, above, sloped] {no} (generate);
\draw[arr] (lookup) -- (exact);
\draw[arr] (generate) -- (cited);

% -- Icons: small monochrome pictograms, 9mm left of each box's west ----
% edge, same hand-drawn-path technique as Chapter 13's figure.
\begin{scope}[shift={($(q.west)+(-9mm,0)$)}, thin]
  \draw (0mm,1.6mm) circle (1.6mm);
  \node[font=\tiny] at (0mm,1.6mm) {?};
\end{scope}
\begin{scope}[shift={($(decision.west)+(-9mm,0)$)}, thin]
  \draw (-0.4mm,0.4mm) circle (1.3mm);
  \draw (0.5mm,-0.5mm) -- (1.6mm,-1.6mm);
\end{scope}
\begin{scope}[shift={($(lookup.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,0.2mm) rectangle (-0.2mm,1.6mm);
  \draw (0.2mm,0.2mm) rectangle (1.6mm,1.6mm);
  \draw (-1.6mm,-1.6mm) rectangle (-0.2mm,-0.2mm);
  \draw (0.2mm,-1.6mm) rectangle (1.6mm,-0.2mm);
\end{scope}
\begin{scope}[shift={($(generate.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,-1mm) rectangle (1.6mm,1.4mm);
  \draw (-0.6mm,-1.6mm) -- (0mm,-1mm) -- (0.6mm,-1.6mm) -- cycle;
  \draw (-1mm,0.6mm) -- (1mm,0.6mm);
  \draw (-1mm,-0.1mm) -- (0.4mm,-0.1mm);
\end{scope}
\begin{scope}[shift={($(exact.west)+(-9mm,0)$)}, thick]
  \draw (-1.4mm,0mm) -- (-0.3mm,-1.3mm) -- (1.6mm,1.6mm);
\end{scope}
\begin{scope}[shift={($(cited.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,-1.6mm) rectangle (1.6mm,1.6mm);
  \draw (-1mm,0.9mm) -- (1mm,0.9mm);
  \draw (-1mm,0mm) -- (1mm,0mm);
  \draw (0.3mm,-1.3mm) -- (1mm,-1.3mm) -- (1mm,-0.7mm);
\end{scope}
\end{tikzpicture}
\end{document}
"""

# Chapter 6's quality gate is the same shape as one node inside Chapter
# 13's daily loop (in fact it's that node's internals) -- a main chain
# ending in a decision with one normal continuation (accept) and one
# exception exit (reject). So it reuses exitColor/exitbox exactly the
# way Chapter 13 did for its own quality-gate node, instead of Chapter
# 10's symmetric two-column treatment (where neither branch was an
# exception). The subtitle quotes the chapter's own mud-check analogy
# rather than inventing new copy.
QUALITY_GATE_TEX = r"""
\documentclass[tikz,border=6pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, calc}
\begin{document}
\begin{tikzpicture}[
  font=\sffamily,
  box/.style={rectangle, rounded corners=2pt, draw, thick, text width=46mm,
    minimum height=9mm, font=\sffamily\small, align=center},
  exitbox/.style={rectangle, rounded corners=2pt, draw=exitColor, thick,
    text width=32mm, minimum height=9mm, font=\sffamily\small,
    align=center, text=exitColor},
  arr/.style={-{Stealth[length=2.2mm]}, thick},
  exitarr/.style={-{Stealth[length=2.2mm]}, thick, exitColor},
  lbl/.style={font=\scriptsize\itshape}
]
\definecolor{exitColor}{HTML}{B8562F}

% -- Title -------------------------------------------------------------
\node[font=\sffamily\Large\bfseries, align=center] (title)
  {The OCR Quality Gate:\\Trust or Reject?};
\node[font=\sffamily\normalsize\itshape, align=center, text width=100mm,
  below=3mm of title] (subtitle)
  {``A mud check before you commit to pumping downhole.''};
\draw[thin] ($(subtitle.south west)+(0,-1.2mm)$) -- ($(subtitle.south east)+(0,-1.2mm)$);

% -- Main chain ----------------------------------------------------------
\node[box, below=13mm of subtitle] (arrive) {Extracted text arrives};
\node[box, below=9mm of arrive] (flags)
  {Check four quality flags\\{\scriptsize\itshape low text density, high symbol ratio,
  repeated garbage, low line count}};
\node[box, below=9mm of flags] (count) {Count how many flags fired};
\node[box, below=9mm of count] (decision) {Two or more active?};
\node[exitbox, right=14mm of decision] (reject) {Reject $\to$\\flag for review};
\node[box, below=9mm of decision] (accept) {Accept into the index};

% -- Arrows --------------------------------------------------------------
\draw[arr] (arrive) -- (flags);
\draw[arr] (flags) -- (count);
\draw[arr] (count) -- (decision);
\draw[arr] (decision) -- node[lbl, left] {no} (accept);
\draw[exitarr] (decision) -- node[lbl, above] {yes} (reject);

% -- Icons ----------------------------------------------------------------
\begin{scope}[shift={($(arrive.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,-2mm) rectangle (1.6mm,2mm);
  \draw (-0.9mm,1mm) -- (0.9mm,1mm);
  \draw (-0.9mm,0mm) -- (0.9mm,0mm);
  \draw (-0.9mm,-1mm) -- (0.4mm,-1mm);
\end{scope}
\begin{scope}[shift={($(flags.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,1mm) rectangle (-0.6mm,2mm);
  \draw (-1.6mm,-0.5mm) rectangle (-0.6mm,0.5mm);
  \draw (-1.6mm,-2mm) rectangle (-0.6mm,-1mm);
  \draw (-0.2mm,1.5mm) -- (1.6mm,1.5mm);
  \draw (-0.2mm,0mm) -- (1.6mm,0mm);
  \draw (-0.2mm,-1.5mm) -- (1.6mm,-1.5mm);
\end{scope}
\begin{scope}[shift={($(count.west)+(-9mm,0)$)}, thick]
  \draw (-1.6mm,-1.6mm) -- (-1.6mm,1.6mm);
  \draw (-0.6mm,-1.6mm) -- (-0.6mm,1.6mm);
  \draw (0.4mm,-1.6mm) -- (0.4mm,1.6mm);
  \draw (1.4mm,-1.6mm) -- (1.4mm,1.6mm);
\end{scope}
\begin{scope}[shift={($(decision.west)+(-9mm,0)$)}, thin]
  \draw (0mm,1.8mm) -- (1.8mm,0mm) -- (0mm,-1.8mm) -- (-1.8mm,0mm) -- cycle;
\end{scope}
\begin{scope}[shift={($(accept.west)+(-9mm,0)$)}, thick]
  \draw (-1.4mm,0mm) -- (-0.3mm,-1.3mm) -- (1.6mm,1.6mm);
\end{scope}
\end{tikzpicture}
\end{document}
"""

# Chapter 8's two indexes aren't sequential the way the old ASCII art's
# single column of downward arrows implied (global index appearing to
# depend on / follow the per-doc index). They're both built independently
# from the same chunks+embeddings step, per the chapter's own prose ("the
# two tiers branch from the same per-document work, then serve different
# questions") -- so this is a fan-out fork, not a decision. It borrows
# Chapter 10's two-column shape but drops the yes/no arrow labels, since
# nothing here is being decided between; both branches happen.
DUAL_INDEX_TEX = r"""
\documentclass[tikz,border=6pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, calc}
\begin{document}
\begin{tikzpicture}[
  font=\sffamily,
  box/.style={rectangle, rounded corners=2pt, draw, thick, text width=44mm,
    minimum height=9mm, font=\sffamily\small, align=center},
  arr/.style={-{Stealth[length=2.2mm]}, thick}
]

% -- Title -------------------------------------------------------------
\node[font=\sffamily\Large\bfseries, align=center] (title)
  {One Pipeline,\\Two Search Indexes};
\node[font=\sffamily\normalsize\itshape, align=center, text width=110mm,
  below=3mm of title] (subtitle)
  {``The two tiers branch from the same per-document work,\\then serve different questions.''};
\draw[thin] ($(subtitle.south west)+(0,-1.2mm)$) -- ($(subtitle.south east)+(0,-1.2mm)$);

% -- Shared chain --------------------------------------------------------
\node[box, below=13mm of subtitle] (pdfs) {76 DDR PDFs};
\node[box, below=9mm of pdfs] (chunk)
  {Chunk + embed\\each report\\{\scriptsize\itshape same per-report work}};

\node[box, below left=16mm and 6mm of chunk] (perdoc)
  {Per-document\\FAISS index\\{\scriptsize\itshape one per report}\\{\scriptsize\itshape search THIS report}};
\node[box, below right=16mm and 6mm of chunk] (global)
  {Global\\FAISS index\\{\scriptsize\itshape 1{,}428 chunks, all reports}\\{\scriptsize\itshape search ACROSS reports}};

% -- Arrows ----------------------------------------------------------------
\draw[arr] (pdfs) -- (chunk);
\draw[arr] (chunk) -- (perdoc);
\draw[arr] (chunk) -- (global);

% -- Icons -------------------------------------------------------------
\begin{scope}[shift={($(pdfs.west)+(-9mm,0)$)}, thin]
  \draw (-1.2mm,-2.2mm) rectangle (2mm,1.8mm);
  \draw (-2mm,-1.8mm) rectangle (1.2mm,2.2mm);
\end{scope}
\begin{scope}[shift={($(chunk.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,0.2mm) rectangle (-0.2mm,1.6mm);
  \draw (0.2mm,0.2mm) rectangle (1.6mm,1.6mm);
  \draw (-1.6mm,-1.6mm) rectangle (-0.2mm,-0.2mm);
  \draw (0.2mm,-1.6mm) rectangle (1.6mm,-0.2mm);
\end{scope}
\begin{scope}[shift={($(perdoc.west)+(-9mm,0)$)}, thin]
  \draw (-1.6mm,0.9mm) rectangle (1.6mm,1.7mm);
  \draw (-1.6mm,-0.4mm) rectangle (1.6mm,0.4mm);
  \draw (-1.6mm,-1.7mm) rectangle (1.6mm,-0.9mm);
\end{scope}
\begin{scope}[shift={($(global.west)+(-9mm,0)$)}, thin]
  \draw (-2mm,-2mm) rectangle (2mm,2mm);
  \draw (-1.4mm,0.7mm) rectangle (1.4mm,1.4mm);
  \draw (-1.4mm,-0.35mm) rectangle (1.4mm,0.35mm);
  \draw (-1.4mm,-1.4mm) rectangle (1.4mm,-0.7mm);
\end{scope}
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
        print("OK: theory_ch13_dailyloop (4-phase flowchart, icons, 2 exit paths)")
        render_tex("theory_ch10_routing", ROUTING_TEX, workdir)
        print("OK: theory_ch10_routing (two-column decision branch, icons)")
        render_tex("theory_ch06_qualitygate", QUALITY_GATE_TEX, workdir)
        print("OK: theory_ch06_qualitygate (main chain + 1 exit path, icons)")
        render_tex("theory_ch08_dualindex", DUAL_INDEX_TEX, workdir)
        print("OK: theory_ch08_dualindex (fan-out fork, icons)")
