# Release notes

Per-release highlights for *Building Industrial RAG Systems from Daily
Drilling Reports*. See [CHANGELOG.md](CHANGELOG.md) for the full history.

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
