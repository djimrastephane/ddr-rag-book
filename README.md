# Building Industrial RAG Systems from Daily Drilling Reports

A hands-on, build-as-you-go book teaching retrieval-augmented generation
(RAG) to drilling and completions engineers, written in the
practical-first spirit of *Python Crash Course*. Readers start with a
folder of real Daily Drilling Report PDFs and finish with an Industrial
DDR Intelligence Platform, one working chapter at a time.

The book source, chapters, and companion code all live in
[`book/`](book/) — see [`book/README.md`](book/README.md) for the full
project layout, quickstart, and chapter map.

**Quickstart:**

```bash
cd book
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
quarto render
```

Companion pipeline: [DDR_UTAH_FORGE](https://github.com/djimrastephane/DDR_UTAH_FORGE).

**License:** code is [MIT](LICENSE); the book's text is
[CC BY 4.0](LICENSE-CONTENT.md).
