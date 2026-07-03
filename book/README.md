# Building Industrial RAG Systems from Daily Drilling Reports

Companion source for the book of the same name — a hands-on, build-as-you-go
guide to retrieval-augmented generation (RAG) for drilling and completions
engineers, written in the practical-first spirit of *Python Crash Course*.

Readers start with a folder of DDR PDFs and finish with an Industrial DDR
Intelligence Platform, one working chapter at a time.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python code/chapter_01/generate_sample_ddr.py   # creates the sample DDR archive
quarto render                                    # builds the book to _book/
```

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
│   └── sample_ddrs/           Synthetic DDR PDFs (generated, not committed)
│
├── notebooks/                 Interactive Jupyter/Quarto companion notebooks
├── figures/                   Book figures and diagrams
└── appendix/
    ├── appendix_a_environment_setup.qmd
    └── appendix_b_oilfield_glossary.qmd
```

## Chapter map

**Part I — Foundations** (synthetic teaching corpus, five sample DDRs,
fully reproducible offline):

| Ch. | Artifact you build |
|---|---|
| 1 | PDF text extraction script |
| 2 | Oilfield abbreviation expansion engine |
| 3 | Keyword search engine (inverted index) |
| 4 | Semantic search (embeddings + cosine similarity) |
| 5 | First RAG pipeline with cited answers |

**Part II — Industrialising the System** (grounded in the real,
production [DDR_RAG_Pipeline](https://github.com/djimrastephane/DDR_RAG_Pipeline)
companion repository — validated against a 171-report, £84.2M drilling
campaign):

| Ch. | Artifact you build |
|---|---|
| 6 | OCR quality gate for scanned reports |
| 7 | Token-based and segment-aware chunking |
| 8 | FAISS vector index (per-doc and global) |
| 9 | Hybrid BM25 + dense retrieval with cross-encoder reranking |
| 10 | Traceable, citation-backed answers with gap detection |
| 11 | Retrieval evaluation harness (recall@k, MRR, NDCG@k) |
| 12 | Cross-well causality and the full Industrial DDR Intelligence Platform |

Each Part II chapter includes a simplified, standalone implementation in
`code/chapter_NN/` (no companion-repo access required to follow along)
plus pointers to the exact files in the full production system.

## Relationship to the companion pipeline repository

This book repository and [DDR_RAG_Pipeline](https://github.com/djimrastephane/DDR_RAG_Pipeline)
are deliberately separate:

- **This repository** teaches the concepts, one small, runnable artifact
  per chapter, starting from zero RAG/embeddings knowledge.
- **DDR_RAG_Pipeline** is the real, production-grade system — the one
  those concepts scale into, validated against a real campaign, with a
  17-page Streamlit dashboard and a FastAPI query endpoint.

Clone them side by side; see [Appendix A, section 6](appendix/appendix_a_environment_setup.qmd#6-cloning-the-companion-pipeline-for-part-ii).

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
