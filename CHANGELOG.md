# Changelog

All notable changes to this book are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This book does not use Semantic Versioning in the strict software sense;
version numbers mark reader-facing milestones (major content additions,
structural changes, or corrections), not API compatibility.

## [Unreleased]

### Added

- A "Reader Contract" section (`book/index.qmd`, README) explaining Part I
  (working prototype) vs. Part II (hardening against real failure modes),
  the separate DDR_UTAH_FORGE companion pipeline's role, and what's out of
  scope (authentication, monitoring, permissions, governance, support
  operations). A matching boundary note was added under the preface's "Why
  industrial" section, plus a compact project map of the sample archive,
  full archive, companion app, and companion pipeline.
- Windows-specific Tesseract/Poppler install guidance in Chapter 6, and
  clearer core/Part II/OCR-only/app-only/notebook-only/testing-only labels
  in `requirements.txt` and `environment.yml`.
- Friendly validation in the book's own code: invalid chunk settings and
  text missing Chapter 1's page markers now raise a clear `ValueError` in
  Chapter 7's `token_chunking.py`; mismatched Reciprocal Rank Fusion
  weights raise in Chapter 9's `hybrid_search.py`; a missing PDF path or a
  nothing-to-save state now fail with a readable message instead of a
  crash in Chapter 13's `ingest.py`. 9 new tests cover these paths (suite
  now 56: 54 passing, 2 skipped without optional pytesseract/streamlit).

### Changed

- Softened the "Cross-well sequence detector" promise (README) to "a
  single-well sequence check, with a path toward cross-well
  intelligence," matching Chapter 12's own careful framing.
- Chapter 5 is now consistently described as producing a working RAG
  *prototype* with known limits, not a finished system (README,
  `index.qmd`, `chapter_05.qmd`).
- Fixed inconsistent heading levels across Chapters 4, 6, 7, 9, 10, and
  the chapter template so every chapter follows H1 → H2 → H3 (`Step N`)
  consistently; reordered Chapter 4's Field Notes to appear after its
  Practical exercise, matching every other chapter's rhythm.
- Shortened an overly technical inline OpenMP/libomp comment in Chapter
  8's `build_faiss_index.py` — the full explanation already lives in the
  chapter's own Production Reality section.
- Clarified in a docstring that Chapter 5's `evidence_excerpts()` returns
  a quick preview, not necessarily the passage that matched (no behavior
  change).

## [1.3.2] - 2026-07-09

### Changed

- Use the author's full name, **Djimra Stephane Soulanoudjingar**,
  throughout: the book author (rendered on every page and the PDF title),
  the content-license attribution line, and the Chicago citation. The
  BibTeX entry and copyright line already used it.

## [1.3.1] - 2026-07-09

### Changed

- Editorial pass to keep the prose plain for the book's stated
  zero-programming audience. Replaced or glossed jargon that appeared
  bare: "idempotent/idempotency" throughout Chapter 13 (now "catch
  duplicates at the door", "never the same one twice", etc.); "corpus"
  across the book (now "archive"); and glossed "heuristic", "context
  window", "regular expression/regex", while rewording "rasterize",
  "concatenated", and "memory/latency". Behaviour and code unchanged;
  test suite still 47 passing.

## [1.3.0] - 2026-07-09

Adds a new Part II finale chapter. See [RELEASE.md](RELEASE.md) for the
full v1.3.0 notes.

### Added

- **Chapter 13: Daily Ingestion** — turns the batch system into a live
  one. `code/chapter_13/ingest.py` ingests one new report PDF by
  *appending* to a live, persisted index (`faiss.IndexFlatIP.add`),
  reusing the book's own Chapter 1/4/6/7/8/10 code, and re-runs the gap
  check. Idempotent on the append-only index. Verified that incremental
  ingestion converges on the identical 333-chunk index a batch build
  produces, with the honest dense-appends / BM25-recomputes lesson.
- `tests/test_chapter_13.py` (3 tests; suite now 47) and a generated
  pipeline diagram for the chapter.

### Changed

- Every chapter's progress strip is now `N / 13`; Part II runs Chapters
  6–13; Chapter 12's closing hands off to Chapter 13, which carries the
  book's finale.

## [1.2.1] - 2026-07-08

### Added

- A real screenshot of the running DDR RAG Companion App on the welcome
  page and README (a question, a cited local-model answer, and the
  retrieved evidence cards), replacing the pending placeholder. Captured
  from the actual app, not a mockup.

### Changed

- The companion app's default top-k is now **3** (was 5) — it matches
  Chapter 5, reduces whole-document noise, and gives the flagship sample
  question a clean cited answer at the default settings.

## [1.2.0] - 2026-07-08

The repository becomes both a technical book and a runnable educational
software project. See [RELEASE.md](RELEASE.md) for the full v1.2.0 notes.

### Added

- **DDR RAG Companion App** (`book/app/streamlit_app.py`) — a small
  Streamlit app that shows the book's payoff end to end: retrieval →
  local-model answer → citations → evidence. It reuses the book's own code
  (Chapters 4, 5, and 9) rather than reimplementing the pipeline, with
  evidence cards (filename, date, score, focused excerpt), a "Why this
  answer?" transparency panel, and a limitations note.
- Local Ollama support for generated answers (default
  `qwen2.5:7b-instruct`, swappable), with a graceful retrieval-only
  fallback and a clear message when Ollama isn't running.
- `book/app/helpers.py` (pure, unit-tested glue), `book/app/README.md`,
  `book/tests/test_app.py` (9 app tests; suite now 44), and `RELEASE.md`.
- A "Companion App" section in the README and a pointer to the app from
  Chapter 5.

### Fixed

- The companion app rebuilds the gitignored extracted-text folder from the
  committed sample PDFs when it's empty, so it runs from a clean clone
  (a fresh checkout previously left the BM25 corpus empty).

## [1.1.2] - 2026-07-07

Clears the non-release-gating items from the publication-readiness audit.

### Fixed

- Reconciled the section-count enumeration against report #38's real
  structure (ten sections: WELL/JOB INFORMATION, BOP, seven data tables,
  and TIME BREAKDOWN). Chapter 1 no longer invents a "remarks" section or
  a wrong seven-item list, and Chapter 7 no longer says "seven" while
  listing ten; Chapter 4's "seven data tables" was already accurate and
  now agrees with the others.
- Removed a duplicated, stranded "Why keyword search fails" section from
  Chapter 3 — it sat after Repository files and repeated both the
  chapter's Field Notes and its Suggested next step. The heading now
  appears only in Chapter 2, and Chapter 3 follows the standard order.

### Changed

- Added Engineering Translation boxes for the code idioms that debut
  unexplained in Chapter 4 for non-programmers — type hints, and
  `np.argsort`/list comprehensions — plus a one-line `lambda` note in
  Chapter 9.
- Added a sample-size caveat in Chapter 11 covering all three metrics:
  at five questions over ten reports the numbers are coarse and show how
  the metrics behave, not a benchmark.

## [1.1.1] - 2026-07-07

### Fixed

- The README's "What You're Building" preview claimed the cross-report
  report-#50 interaction was "the terminal output you'll see once you've
  built the system in Chapter 5" — the same overpromise removed from the
  welcome page in 1.1.0, since Part I's whole-document retrieval can't
  retrieve report #50. Reframed as the finished system's destination, to
  match the welcome page.
- Reconciled a contradiction between Chapter 4's rule (keyword search uses
  expanded text, embeddings use raw) and Chapter 9's BM25 defaulting to
  raw text. Added a verified note: the exercise's own queries are
  unaffected at the top (report #49 tops "packers fishing", report #38
  tops "stuck pipe" either way), but an abbreviation query like "bottom
  hole assembly" genuinely differs — so a production sparse signal uses
  the expanded text, exactly as Chapter 4 concluded.
- Made the pending-app-screenshot state reader-visible on the welcome
  page and README, rather than only in an author-only HTML comment.

### Changed

- Chapter 5 now notes explicitly that `qwen2.5:7b-instruct` is only a
  default — any pulled Ollama model, or a hosted API, works via
  `ollama_llm_call(model=...)`.
- Expanded the acknowledgements' AI-tools disclosure to cover the
  educational approach and iterative review, and to state that all
  engineering decisions, implementation choices and final content remain
  the author's responsibility.

## [1.1.0] - 2026-07-07

A revision pass answering an editorial review, focused on making the book
run what it claims and say only what it can reproduce.

### Added

- Chapter 5 now generates for real, not just a stub. `first_rag.py` gains
  `ollama_llm_call()` — a local-LLM path via Ollama (`qwen2.5:7b-instruct`),
  standard library only, no report text leaving the machine, with a
  graceful fallback if Ollama isn't running — and `evidence_excerpts()`. A
  new Step 4 gives the exact setup commands and a real captured sample
  answer grounded in report #49, labeled non-deterministic.
- Chapter 9 ships a runnable ranked sparse retriever
  (`code/chapter_09/sparse_ranking.py`, BM25 with a term-frequency
  fallback) and a `hybrid_search()` orchestration, so the Chapter 9 and
  Chapter 11 practical exercises run end to end — they previously asked
  readers to fuse a ranked sparse list that didn't exist.
- Chapter 6 gains a real OCR round-trip
  (`code/chapter_06/make_scanned_example.py`): it rasterizes a real report
  to an image-only PDF, shows digital extraction returning nothing,
  recovers the text with OCR, and scores both through the quality gate —
  replacing the hypothetical degraded string as the chapter's main
  example. Adds `pytesseract` and `pdf2image` as Chapter-6-only
  dependencies.
- A qualified "Management view: why this matters" section and a "What this
  becomes" pointer (with an honest screenshot placeholder, no invented
  image) on the welcome page and README.

### Changed

- The welcome page's "what led to the fishing operation on report #50"
  interaction is now framed as the finished system's destination, not
  something Chapter 5 reproduces — Part I's whole-document retrieval
  provably can't retrieve report #50.
- Resolved the `ddr_text` vs `ddr_text_expanded` inconsistency with a
  measured Chapter 4 Field Note: abbreviation expansion helps keyword
  search but only narrowly helps semantic search (report #38 moves from
  rank 2 to rank 1 on "bottom hole assembly", unchanged on "stuck pipe"),
  so keyword search uses the expanded text and embeddings use the raw
  text — and the book now measures why instead of contradicting itself.
- Converted the repeated implementation-step scaffolding headings (What
  problem are we solving?, Inputs, Expected Output, What just happened?)
  from H2 headings to bold lead-ins across all chapters, fixing a
  malformed heading hierarchy that produced duplicated HTML anchors and
  cluttered the HTML and PDF tables of contents.

### Fixed

- Chapter 9's Field Notes previously said its BM25/fusion ranks couldn't
  be reproduced with the book's own code. The new sparse retriever
  reproduces them exactly (report #39: 9th on BM25 alone, 9th fused at
  2.0/0.5, 7th at 1.0/1.0), so the caveat now points readers to run it
  themselves.

## [1.0.4] - 2026-07-07

### Changed

- Revised the Acknowledgements' opening paragraph, and moved the note on
  the author's ideas/technical validation and AI-tool use to the end of
  the section.

### Fixed

- Updated the README's "Latest stable release" link, which was never
  bumped through v1.0.1/v1.0.2/v1.0.3 and still pointed at v1.0.0.

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
