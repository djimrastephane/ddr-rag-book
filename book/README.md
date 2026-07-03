# Building Industrial RAG Systems from Daily Drilling Reports

Companion source for the book of the same name — a hands-on, build-as-you-go
guide to retrieval-augmented generation (RAG) for drilling and completions
engineers, written in the practical-first spirit of *Python Crash Course*.

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

See [Appendix A](appendix/appendix_a_environment_setup.qmd) for full setup
instructions, Positron IDE configuration, and Docker instructions.

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
│   └── chapter_NN/
│       ├── *.py              Runnable scripts referenced in the chapter
│       └── challenge/         Reference solutions to challenge exercises
│
├── datasets/
│   ├── sample_ddrs/           10 real, curated Utah FORGE DDR PDFs (Part I)
│   └── forge_archive/         Full 76-report Utah FORGE archive (Part II)
│
├── notebooks/                 Interactive Jupyter/Quarto companion notebooks
├── figures/                   Book figures and diagrams
└── appendix/
    ├── appendix_a_environment_setup.qmd
    └── appendix_b_oilfield_glossary.qmd
```

## Chapter map

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
archive — real per-document extraction, a real 76-document/2,943-chunk
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
against the committed `datasets/` archive. See [Appendix A, section 6](appendix/appendix_a_environment_setup.qmd#6-the-companion-pipeline-for-part-ii)
for how to clone it and how the two projects relate.

## Recommended workflow in Positron

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

## License

TBD — add a license before publishing or open-sourcing this repository.
