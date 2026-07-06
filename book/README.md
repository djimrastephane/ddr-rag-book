# Building Industrial RAG Systems from Daily Drilling Reports

Companion source for the book of the same name — a hands-on, build-as-you-go
guide that teaches retrieval-augmented generation (RAG) to drilling and
completions engineers, assuming no prior programming experience.

Readers start with a folder of DDR PDFs and finish with an Industrial DDR
Intelligence Platform, one working chapter at a time — using real,
publicly available Daily Drilling Reports from Utah FORGE (a
DOE-funded geothermal research well) throughout.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

quarto render                       # builds the book to _book/
```

The sample DDR archive is already committed under `datasets/` — no
generation or download step needed.

New to Python or unsure where to start? **Part 0 — Preparing Your Python
Workshop** (`chapters/chapter_00.qmd`) walks through the setup above one
command at a time, with plain-English explanations and no assumed prior
experience. It works with any editor — Jupyter Notebook, VS Code, PyCharm
Community, Positron, or a terminal alone — with a short dedicated guide
for each in Appendices A1–A5. [Appendix
A](appendix/appendix_a_environment_setup.qmd) covers what's left: the
sample dataset, rendering the book, and the companion pipeline.

## Project structure

```
book/
├── _quarto.yml              Quarto book configuration
├── index.qmd                Welcome / front page
├── preface.qmd
├── acknowledgements.qmd
├── references.bib           Bibliography
├── custom.scss               HTML theme overrides
│
├── chapters/                 One .qmd per chapter (see below)
├── templates/
│   └── chapter_template.qmd  Copy this to draft a new chapter
│
├── code/                     One subfolder per chapter, e.g. code/chapter_01/
│   ├── setup_check.py        Part 0's one-line environment check
│   └── chapter_NN/
│       ├── *.py              Runnable scripts referenced in the chapter
│       └── challenge/         Reference solutions to challenge exercises
│
├── tests/                     pytest suite exercising every chapter's real code
│   ├── conftest.py            Shared fixtures (sample archive paths, sys.path setup)
│   └── test_chapter_NN.py     One file per chapter with testable code
├── pytest.ini                 pytest configuration (testpaths, markers)
│
├── datasets/
│   ├── sample_ddrs/           10 real, curated Utah FORGE DDR PDFs (Part I)
│   └── forge_archive/         Full 76-report Utah FORGE archive (Part II)
│
├── notebooks/                 Interactive Jupyter/Quarto companion notebooks
├── figures/                   Book figures and diagrams
└── appendix/
    ├── appendix_a_environment_setup.qmd    Dataset, rendering, companion pipeline
    ├── appendix_a1_jupyter.qmd             Jupyter Notebook guide
    ├── appendix_a2_vscode.qmd              VS Code guide
    ├── appendix_a3_pycharm.qmd             PyCharm Community guide
    ├── appendix_a4_positron.qmd            Positron guide
    ├── appendix_a5_terminal.qmd            Terminal-only guide
    └── appendix_b_oilfield_glossary.qmd
```

## Chapter map

**Part 0 — Preparing Your Python Workshop** (`chapters/chapter_00.qmd`):
environment setup for readers with no prior programming experience,
IDE-agnostic — Jupyter Notebook, VS Code, PyCharm Community, Positron, or
terminal only, each with a short dedicated guide in Appendices A1–A5.

**Part I — Foundations** (10 real, curated Utah FORGE DDRs — a genuine
stuck-pipe event, a packers-fail-to-fishing sequence, and more — fully
reproducible offline):

| Ch. | Artifact you build |
|---|---|
| 1 | PDF text extraction script |
| 2 | Oilfield abbreviation expansion engine |
| 3 | Keyword search engine (inverted index) |
| 4 | Semantic search (embeddings + cosine similarity) |
| 5 | First RAG pipeline with cited answers |

**Part II — Industrialising the System** (grounded in **DDR_UTAH_FORGE**,
a companion pipeline built specifically against this book's public
archive — real per-document extraction, a real 76-document/1,428-chunk
global index, and real, verified structural findings like the archive's
genuine reporting gap):

| Ch. | Artifact you build |
|---|---|
| 6 | OCR quality gate for scanned reports |
| 7 | Token-based and segment-aware chunking |
| 8 | FAISS vector index (per-doc and global) |
| 9 | Hybrid BM25 + dense retrieval with fusion weighting |
| 10 | Traceable, citation-backed answers with gap detection |
| 11 | Building your own retrieval evaluation set (recall@k, MRR, NDCG@k) |
| 12 | Sequence detection and the path to cross-well intelligence |

Each Part II chapter includes a simplified, standalone implementation in
`code/chapter_NN/` (no companion-pipeline access required to follow
along) plus pointers to the exact files in the full pipeline. Where a
chapter states a specific number or result, it was independently
verified against the pipeline's real output before being written down —
this book does not present fabricated or borrowed results as if they came
from this archive.

## Relationship to the companion pipeline

[**DDR_UTAH_FORGE**](https://github.com/djimrastephane/DDR_UTAH_FORGE) is
a separate, public repository from this book. This book's own code never
depends on it — every chapter's `code/chapter_NN/` scripts run standalone
against the committed `datasets/` archive. See [Appendix A, section 3](https://djimrastephane.github.io/ddr-rag-book/appendix/appendix_a_environment_setup.html#the-companion-pipeline-for-part-ii)
for how to clone it and how the two projects relate.

## Recommended workflow in Positron (for authors drafting new chapters)

This section describes the author's own workflow for *writing* new
chapters — it is not a requirement for readers. Readers following the
book should start with Part 0 and Appendices A1–A5, which cover five
different editors on equal footing.

1. Open `book/` as the Positron workspace root.
2. Create and select the `.venv` interpreter (see Quickstart above).
3. Draft a chapter in `chapters/chapter_NN.qmd`, starting from
   `templates/chapter_template.qmd`.
4. Develop and test the chapter's code as a plain script in
   `code/chapter_NN/` first — run it from the Positron console — then
   move working code blocks into the `.qmd` once verified.
5. Use `quarto preview chapters/chapter_NN.qmd` for live-reloading a
   single chapter while writing.
6. Run `quarto render` before committing, to catch any chapter that
   fails to execute end to end.

## Reproducing the whole book

```bash
pip install -r requirements.txt
quarto render
```

Output is written to `_book/`. No API keys or paid services are required
for Part I; Chapter 5's `llm_call` argument is provider-agnostic — plug in
a local or hosted model of your choice.

## Running tests

`tests/` exercises the real functions in every chapter's `code/chapter_NN/`
script against the real sample DDR archive — the same `extract_text()`,
`expand_text()`, `search()`, `evaluate_ocr_quality()`, and so on that the
chapters themselves document, not simplified stand-ins. CI runs the full
suite on Linux, Windows, and macOS on every push and pull request that
touches `book/**` (see `.github/workflows/tests-linux.yml`,
`tests-windows.yml`, `tests-macos.yml`).

```bash
pip install -r requirements.txt
pytest -v
```

Tests marked `slow` (Chapters 4, 5, 7, 8) download a small embedding
model and a tokenizer's vocabulary file on first run; skip them locally
with `pytest -v -m "not slow"` if you're offline.

## License

Code (`code/`, `notebooks/`) is licensed under the [MIT License](../LICENSE).
The book's text (chapters, preface, appendices) is licensed under
[CC BY 4.0](../LICENSE-CONTENT.md). The Utah FORGE DDR data in `datasets/`
is public DOE-funded research data, not covered by either license.
