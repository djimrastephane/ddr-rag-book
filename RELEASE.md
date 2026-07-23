# Release notes

Per-release highlights for *Building Industrial RAG Systems from Daily
Drilling Reports*. See [CHANGELOG.md](CHANGELOG.md) for the full history.

## v1.4.0

A reader-trust pass: an explicit contract with the reader up front, a
full first-use jargon audit across every chapter, and proper setup
coverage for the one dependency that had none.

### Added

- **A "Reader Contract" section** (`book/index.qmd`, README) explaining
  Part I (working prototype) vs. Part II (hardening against real
  failure modes), the separate DDR_UTAH_FORGE companion pipeline's role,
  and what's deliberately out of scope (authentication, monitoring,
  permissions, governance, support operations). A matching boundary
  note under the preface's "Why industrial" section, plus a compact
  project map of the sample archive, full archive, companion app, and
  companion pipeline.
- **A first-use jargon audit across all 13 chapters** — "Engineering
  Translation" callouts or light inline glosses for terms used before
  they were defined: `token` (Chapter 3, flagging its different sense
  for Chapter 7), `chunk` (Chapter 4), the embedding-model-vs-language-
  model distinction and `hallucination` (Chapter 5), `OCR` and `false
  positive` (Chapter 6), `None` (Chapter 1), `API`/`hardcoded`/
  `deterministic` (Chapters 4–5), the reused meaning of `index`
  (Chapter 8), `hybrid retrieval`/`NaN`/`lexical` (Chapter 9),
  `shadowing`/`ISO date strings`/`boilerplate` (Chapter 10), `ground
  truth` (Chapter 11), and `NLP` (Chapter 2). Also corrected a
  misattributed formula name — the classic BM25 IDF weighting is
  Robertson–Spärck Jones, not "Robertson-Sparse-Selection."
- **A proper Ollama install/verify walkthrough** in Chapter 5:
  platform-specific install steps, an `ollama --version` check with
  expected output, and a download-size/RAM callout — plus two new
  Ollama troubleshooting rows in Appendix A and a README note that any
  pulled model works, not just the documented default.
- Windows-specific Tesseract/Poppler install guidance in Chapter 6, and
  clearer dependency labels (core/Part II/OCR-only/app-only/notebook-
  only/testing-only) in `requirements.txt` and `environment.yml`.
- Friendly validation in the book's own code: invalid chunk settings and
  missing page markers now raise clear errors in Chapter 7's
  `token_chunking.py`; mismatched fusion weights raise in Chapter 9's
  `hybrid_search.py`; a missing PDF path or nothing-to-save state fails
  with a readable message in Chapter 13's `ingest.py`. 9 new tests
  (suite now 56: 54 passing, 2 skipped without optional
  pytesseract/streamlit).

### Changed

- Softened the "Cross-well sequence detector" promise to "a single-well
  sequence check, with a path toward cross-well intelligence," matching
  Chapter 12's own careful framing.
- Chapter 5 is now consistently described as producing a working RAG
  *prototype* with known limits, not a finished system.
- Fixed inconsistent heading levels across Chapters 4, 6, 7, 9, 10, and
  the chapter template so every chapter follows H1 → H2 → H3 (`Step N`)
  consistently; reordered Chapter 4's Field Notes to match every other
  chapter's rhythm.
- Fixed two callout-placement regressions the jargon audit introduced:
  Chapter 5's Theory had stacked into three consecutive callout boxes
  with no prose between them; Chapter 4's "Chunk" and "API" callouts
  each interrupted an established structural pattern.
- Shortened an overly technical inline OpenMP/libomp comment in Chapter
  8 — the full explanation already lives in the chapter's own
  Production Reality section.
- README hardware requirements now flag Ollama's extra ~5 GB disk / RAM
  footprint.

## v1.3.2

### Changed

- Uses the author's full name, **Djimra Stephane Soulanoudjingar**,
  consistently — the book author (rendered on every page and the PDF title
  page), the content-license attribution line, and the Chicago citation.

## v1.3.1

A plain-language editorial pass, keeping the prose accessible to the
book's zero-programming audience.

### Changed

- Replaced or glossed jargon that appeared without explanation:
  **"idempotent/idempotency"** throughout Chapter 13 (now plain terms like
  "catch duplicates at the door" and "never the same one twice");
  **"corpus"** across the book (now "archive"); and glossed **"heuristic"**,
  **"context window"**, and **"regular expression / regex"**, while
  rewording **"rasterize"**, **"concatenated"**, and **"memory/latency"**.
- Terms the book already defines at first use or teaches via Engineering
  Translation callouts (metadata, sparse/dense, embeddings, tokens, BM25,
  cross-encoder…) were left as-is. Behaviour and code unchanged; test
  suite still 47 passing.

## v1.3.0

Adds **Chapter 13 — Daily Ingestion**, a new Part II finale that turns the
batch system into a live one.

### Added

- **Chapter 13: Daily Ingestion.** `code/chapter_13/ingest.py` ingests one
  new report PDF by *appending* to a live, persisted index
  (`faiss.IndexFlatIP.add`), reusing the book's own code end to end:
  extract (Ch 1) → quality gate (Ch 6) → chunk (Ch 7) → embed (Ch 4) →
  append (Ch 8) → re-run the gap check (Ch 10). Idempotent on the
  append-only index.
- The chapter's two verified lessons: incremental ingestion converges on
  the **identical** index a batch build produces (296 → 333 chunks, the
  exact Chapter 8 total), and the honest asymmetry that **the dense index
  appends but BM25 recomputes**.
- `tests/test_chapter_13.py` (3 tests; suite now 47 passing) and a
  generated pipeline diagram for the chapter.

### Changed

- Every chapter's progress strip is now `N / 13`; Part II runs Chapters
  6–13; Chapter 12's closing hands off to Chapter 13, which now carries
  the book's finale.

## v1.2.1

A small follow-up to the companion app.

### Added

- A real screenshot of the running DDR RAG Companion App on the welcome
  page and README — a question, a cited local-model answer, and the
  retrieved evidence cards. Captured from the actual app, not a mockup.

### Changed

- The companion app's default top-k is now **3** (was 5): it matches
  Chapter 5, reduces whole-document noise, and gives the flagship sample
  question a clean cited answer at the default settings.

## v1.2.0

The repository is now both a technical book and a runnable educational
software project: this release adds a small companion app that
demonstrates the book's payoff end to end.

### New

- **Companion Streamlit app** (`book/app/streamlit_app.py`) — ask one
  engineering question against the sample DDR archive and see retrieval →
  answer → citations → evidence. Reuses the book's own code (Chapters 4,
  5, and 9); it does not reimplement the pipeline.
- **Local Ollama support for generated answers** — default model
  `qwen2.5:7b-instruct`, swappable in the sidebar. No report text leaves
  your machine.
- **Retrieval-only mode when Ollama is unavailable** — the app never
  crashes on a missing model; it shows the retrieved evidence and a clear
  message: *"Ollama is not running. Retrieval still works. Start Ollama to
  generate an answer."*
- **Evidence cards** with report filename, date, retrieval score, and a
  focused excerpt (plus a safe, derived "why it matters" line).
- **"Why this answer?" transparency panel** — the query, the ranked
  retrieved reports, the evidence snippets, whether the answer was
  generated or retrieval-only, and the exact prompt sent to the model.
- **Companion app README and run commands** (`book/app/README.md`).

### Improved

- **README onboarding for the companion app** — a new "Companion App"
  section with run commands and the retrieval-vs-generation distinction.
- **Educational local-first workflow** — everything runs locally against
  the committed sample archive.
- **Clear distinction between retrieval and generation** — retrieval
  always runs; generation is an explicit, optional step gated on a local
  model being available.

### Known limitations

- The app uses the **10-report sample archive**, not the full 76-report
  archive.
- Retrieval **re-embeds the sample reports per query** (fast at this
  scale; the embedding model itself is cached).
- Generated answers depend on **local Ollama model behavior** and are
  non-deterministic.
- **Cross-report questions** (tracing a cause in one report to an outcome
  in the next) may still need chunk-level retrieval and reranking; they
  can strain here.
- This is **not a production system** — no upload, auth, database, or
  multi-user support, and no security model. Always verify answers against
  the original report before using them for engineering decisions.

### Planned (v1.3.0 or v2.0)

- Chunk-level retrieval (Chapter 8's FAISS chunk index).
- True page citations (Chapter 10's `citations_from_search`).
- Cached embeddings, not just the cached model.
- Per-signal ranking display (BM25 vs dense) in the transparency panel.
- Better citation copy / export.
