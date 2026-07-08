# DDR RAG Companion App

A small Streamlit app that shows the book's final payoff end to end: ask
one engineering question against the sample Daily Drilling Report archive
and see **retrieval → local-model answer → citations → the original
evidence**. Evidence first, answer second.

This is an educational companion, not a production system. It runs on the
ten-report public sample archive that ships with the book.

## Run it

From the repository root, with the book's virtual environment active:

```bash
pip install -r book/requirements.txt      # includes Streamlit
ollama pull qwen2.5:7b-instruct           # for generated answers (optional)
streamlit run book/app/streamlit_app.py
```

Streamlit opens the app in your browser. Pick a sample question (or type
your own) in the sidebar and press **Ask**.

## Ollama is optional

- **Retrieval always works** without Ollama — you'll see the matched
  reports, scores, and evidence excerpts.
- **Generated answers require Ollama.** If it isn't running, the app says
  so plainly and shows the retrieved evidence anyway:
  *"Ollama is not running. Retrieval still works. Start Ollama to generate
  an answer."*

Install Ollama from [ollama.com](https://ollama.com), then
`ollama pull qwen2.5:7b-instruct` and `ollama serve`. Any pulled model
works — change the model name in the sidebar. No report text leaves your
machine.

## What it reuses from the book

Nothing here reimplements the pipeline. The app imports the book's own
code:

| Step | Comes from |
|---|---|
| Hybrid retrieval (BM25 + dense) | `code/chapter_09/hybrid_search.py` |
| Prompt assembly + local generation | `code/chapter_05/first_rag.py` |
| Embedding model + report loading | `code/chapter_04/semantic_search.py` |

`app/helpers.py` holds the small app-only logic (evidence snippets, date
parsing, the Ollama check, and the `run_query` glue). `app/streamlit_app.py`
is only the screen around it.

## Limitations

This app is for learning. It runs on a small public sample archive.
Cross-report questions (e.g. tracing a cause in one report to an outcome
in the next) are the hard case the book's Part II is built to handle;
here they can strain. Always verify answers against the original report
before using them for engineering decisions — the engineer remains
responsible for the call.

## Files

| File | Purpose |
|---|---|
| `streamlit_app.py` | The UI: pipeline visual, question, answer, evidence cards, "Why this answer?" panel |
| `helpers.py` | Retrieval/generation glue and evidence-snippet logic (no Streamlit; unit-tested) |
