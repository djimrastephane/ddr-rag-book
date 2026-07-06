# Changelog

All notable changes to this book are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This book does not use Semantic Versioning in the strict software sense;
version numbers mark reader-facing milestones (major content additions,
structural changes, or corrections), not API compatibility.

## [Unreleased]

## [1.0.3] - 2026-07-06

### Fixed

- Corrected the companion pipeline's real global-index chunk count
  throughout the book, its READMEs, and the Chapter 8 challenge script:
  2,943 was wrong, the real figure (224 tokens/56-token overlap) is
  1,428 — updated every citation, and reworded the Operational Problem
  framing so it reads as a reported fact rather than an instruction
  readers could reproduce themselves.
- Fixed three independently-verified factual bugs found by rerunning
  this book's own bundled code against its real data: Chapter 2 claimed
  report #38 writes "BHA" 21 times (the real count is 9 — "21" in the
  source is the BHA's own equipment ID, not an occurrence count);
  Chapter 4's line-level cosine-similarity Field Notes used non-verbatim,
  partly fabricated line text that produced an artificial "clean tie"
  which doesn't exist in the real report text (rewritten with verbatim
  quotes and real scores, including the matching
  `code/chapter_04/challenge/` reference script and its pytest test);
  Chapter 5's fishing-operation ranking table had the wrong report at
  rank 3 and no score matching current reproducible output (refreshed
  against the pinned model/library versions).
- Fixed Appendix B's oilfield glossary: five terms (BOP, DP, MW, PBTD,
  TD) are genuinely present in the real sample archive but weren't
  tagged `(FORGE)` — MW's omission directly contradicted Chapter 2's own
  abbreviation dictionary. STK was defined as "stuck," but every real
  occurrence is a pump-spec table header meaning "stroke length,"
  corrected accordingly.
- Fixed Appendix A's `DDR_UTAH_FORGE` clone instructions, which told
  readers to `cd ..` from `book/` to reach a neutral "projects root" —
  that directory is actually the root of this book's own git repository,
  so the clone landed inside it, contradicting the surrounding "clone it
  alongside... not inside it" instruction.
- Reworded `requirements.txt`/`environment.yml` comments that attributed
  `rank-bm25` and `pandas`/`pyarrow` to specific book chapters: none of
  the three are imported anywhere in this book's own bundled code (they
  support experimenting with the companion pipeline's real BM25 index
  and `ddr_facts.parquet` directly). Also aligned `environment.yml`'s
  `pyarrow`/`pytest` version pins with `requirements.txt`, and removed
  `pandas` from the Acknowledgements' list of tools this book's own code
  relies on, for the same reason.
- Added honest caveats to several other companion-pipeline-attributed
  numbers (Chapter 9's BM25/RRF rankings, Chapter 10's
  `ddr_facts.parquet` rows, Chapter 12's `causality_analyzer.py`
  thresholds, Chapter 6's pre-deduplication source-file count) clarifying
  they're reported facts from a pipeline outside this repository, not
  something reproducible with this book's own bundled code.

## [1.0.2] - 2026-07-06

### Fixed

- Corrected the FAISS paper's citation year: `johnson2019faiss` listed
  2019, but the paper's actual arXiv submission was 2017 (confirmed via
  arXiv/DBLP) — renamed the key to `johnson2017faiss` to match.
- Fixed the hallucination survey citation (`ji2023hallucination`) to use
  ACM Computing Surveys' real article-number format (article 248, DOI
  10.1145/3571730) instead of an incorrect page range.

## [1.0.1] - 2026-07-06

### Added

- README now links to the latest stable release and `CHANGELOG.md`, and
  notes that the live site tracks `main`, which can be ahead of the most
  recently tagged release.

## [1.0.0] - 2026-07-06

### Added

- Full 13-chapter curriculum (Part 0 environment setup through Chapter 12)
  teaching retrieval-augmented generation from first principles: PDF text
  extraction, abbreviation expansion, keyword search, semantic search, a
  first end-to-end RAG system, OCR quality gating, token chunking, FAISS
  indexing, hybrid BM25 + dense retrieval, traceable citations, retrieval
  evaluation, and torque-trend/sequence detection.
- Six appendices: environment setup and per-editor guides (Jupyter,
  VS Code, PyCharm, Positron, terminal) plus an oilfield glossary.
- Every chapter's pipeline explained with TikZ-rendered diagrams
  (light/dark themed for HTML, PDF-safe for print), chapter status strips
  (progress, estimated time, difficulty badge), named-persona operational
  problems, CHECKPOINT and WHAT YOU BUILT boxes, and Field Notes grounded
  in the real archive.
- Traceable citations wired end-to-end through the real pipeline: report,
  page, and date are read from actual extraction/chunking/indexing output,
  never hand-typed, and deduplicated by (report, page) so a repeated
  source isn't miscounted as independent evidence.
- All content verified against a real, public Utah FORGE Daily Drilling
  Report archive — no invented case studies or fabricated examples.
- Dual HTML (light/dark theme) and PDF output via Quarto, auto-published
  to GitHub Pages on every push to `main`.
- Full pytest suite covering every chapter's code.
