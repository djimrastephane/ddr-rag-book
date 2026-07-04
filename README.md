# Building Industrial RAG Systems from Daily Drilling Reports

This repository contains the chapters, code, and sample data for **Building Industrial RAG Systems from Daily Drilling Reports** — a hands-on, build-as-you-go book that teaches retrieval-augmented generation (RAG) to drilling and completions engineers, assuming zero prior programming experience.

<br>
<br>

<a href="https://djimrastephane.github.io/ddr-rag-book/"><img src="book/figures/cover.jpg" width="250px"></a>

<br>

In *Building Industrial RAG Systems from Daily Drilling Reports*, you'll build a working RAG system from scratch, one chapter at a time: extracting text from a real Daily Drilling Report (DDR) PDF, expanding oilfield shorthand, searching an archive by keyword and then by meaning, and finally generating cited, evidence-backed answers to real engineering questions — no machine learning background assumed, no black-box product involved.

Every example in the book uses real, publicly available Daily Drilling Reports from **Utah FORGE** — a Department of Energy-funded enhanced geothermal system research well (FORGE 16A(78)-32) — not synthetic stand-ins. A real stuck-pipe event, a real packers-fail-to-fishing sequence, and a real reporting gap all appear exactly as filed.

- Link to the [official source code repository](https://github.com/djimrastephane/ddr-rag-book)
- [Read the book online](https://djimrastephane.github.io/ddr-rag-book/)
- License: code is [MIT](LICENSE); the book's text is [CC BY 4.0](LICENSE-CONTENT.md)

<br>
<br>

To download a copy of this repository, click the [Download ZIP](https://github.com/djimrastephane/ddr-rag-book/archive/refs/heads/main.zip) button, or run the following in your terminal:

```bash
git clone https://github.com/djimrastephane/ddr-rag-book.git
```

<br>
<br>

# Table of Contents

Please note that this `README.md` file is a Markdown (`.md`) file — GitHub renders it automatically, and if you downloaded this repository as a ZIP, any Markdown previewer will too. The book's chapters, however, are written as `.qmd` (Quarto Markdown) files, which GitHub's file viewer shows as plain unformatted source. Read them properly formatted at [djimrastephane.github.io/ddr-rag-book](https://djimrastephane.github.io/ddr-rag-book/), which renders automatically from this repository.

For the full repository layout (folder tree, part/chapter file map) see [`book/README.md`](book/README.md).

<br>
<br>

> **Tip:**
> If you've never installed Python, never opened a terminal, or aren't sure which editor to use, start with **Part 0 — Preparing Your Python Workshop** ([`book/chapters/chapter_00.qmd`](book/chapters/chapter_00.qmd), or [read it online](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_00.html)). It's IDE-agnostic — Jupyter Notebook, VS Code, PyCharm Community, Positron, or a terminal alone all work identically, each with its own short guide in Appendices A1–A5.

<br>
<br>

[![Publish book to GitHub Pages](https://github.com/djimrastephane/ddr-rag-book/actions/workflows/publish.yml/badge.svg)](https://github.com/djimrastephane/ddr-rag-book/actions/workflows/publish.yml)

- [Troubleshooting](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_00.html#troubleshooting) (Part 0, Section 0.11), plus [Appendix A, Section 5](https://djimrastephane.github.io/ddr-rag-book/appendix/appendix_a_environment_setup.html#troubleshooting) for rendering/dependency issues

Chapter titles in the table below link to the rendered, readable page for that reason.

| Chapter | Main Code (Quick Access) | All Code + Supplementary |
|---|---|---|
| [Part 0: Preparing Your Python Workshop](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_00.html) | [setup_check.py](book/code/setup_check.py) | - |
| [Ch 1: Reading Your First DDR](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_01.html) | - [read_ddr.py](book/code/chapter_01/read_ddr.py)<br/>- [chapter_01_explore.ipynb](book/notebooks/chapter_01_explore.ipynb) | [./book/code/chapter_01](book/code/chapter_01) |
| [Ch 2: Cleaning Operational Text](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_02.html) | - [expand_abbreviations.py](book/code/chapter_02/expand_abbreviations.py)<br/>- [chapter_02_explore.ipynb](book/notebooks/chapter_02_explore.ipynb) | [./book/code/chapter_02](book/code/chapter_02) |
| [Ch 3: Searching DDRs](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_03.html) | - [keyword_search.py](book/code/chapter_03/keyword_search.py)<br/>- [chapter_03_explore.ipynb](book/notebooks/chapter_03_explore.ipynb) | [./book/code/chapter_03](book/code/chapter_03) |
| [Ch 4: Semantic Search](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_04.html) | - [semantic_search.py](book/code/chapter_04/semantic_search.py)<br/>- [chapter_04_explore.ipynb](book/notebooks/chapter_04_explore.ipynb) | [./book/code/chapter_04](book/code/chapter_04) |
| [Ch 5: First RAG System](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_05.html) | - [first_rag.py](book/code/chapter_05/first_rag.py)<br/>- [chapter_05_explore.ipynb](book/notebooks/chapter_05_explore.ipynb) | [./book/code/chapter_05](book/code/chapter_05) |
| [Ch 6: Scanned Reports and OCR Quality Gates](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_06.html) | - [ocr_quality_gate.py](book/code/chapter_06/ocr_quality_gate.py) | [./book/code/chapter_06](book/code/chapter_06) |
| [Ch 7: Chunking That Respects Report Structure](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_07.html) | - [token_chunking.py](book/code/chapter_07/token_chunking.py) | [./book/code/chapter_07](book/code/chapter_07) |
| [Ch 8: Vector Databases at Scale](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_08.html) | - [build_faiss_index.py](book/code/chapter_08/build_faiss_index.py)<br/>- [build_full_archive.py](book/code/chapter_08/build_full_archive.py) | [./book/code/chapter_08](book/code/chapter_08) |
| [Ch 9: Hybrid Retrieval and Reranking](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_09.html) | - [hybrid_search.py](book/code/chapter_09/hybrid_search.py) | [./book/code/chapter_09](book/code/chapter_09) |
| [Ch 10: Traceable Answers and Hallucination Mitigation](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_10.html) | - [traceable_answers.py](book/code/chapter_10/traceable_answers.py) | [./book/code/chapter_10](book/code/chapter_10) |
| [Ch 11: Evaluating Retrieval Quality](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_11.html) | - [eval_metrics.py](book/code/chapter_11/eval_metrics.py) | [./book/code/chapter_11](book/code/chapter_11) |
| [Ch 12: Sequence Detection: Building Toward Cross-Well Intelligence](https://djimrastephane.github.io/ddr-rag-book/chapters/chapter_12.html) | - [torque_trend_check.py](book/code/chapter_12/torque_trend_check.py) | [./book/code/chapter_12](book/code/chapter_12) |
| [Appendix A: Environment Setup](https://djimrastephane.github.io/ddr-rag-book/appendix/appendix_a_environment_setup.html) | - | [./book/appendix](book/appendix) |
| Appendices A1–A5: Jupyter / VS Code / PyCharm / Positron / Terminal-only | - | [./book/appendix](book/appendix) |
| [Appendix B: Oilfield Abbreviation Glossary](https://djimrastephane.github.io/ddr-rag-book/appendix/appendix_b_oilfield_glossary.html) | - | [appendix_b_oilfield_glossary.qmd](book/appendix/appendix_b_oilfield_glossary.qmd) |

<br>
&nbsp;

## Prerequisites

The only real prerequisite is curiosity. This book assumes zero prior programming or AI/ML experience — Part 0 takes you from nothing installed to a working Python environment, and every concept, down to what a function or a dictionary is, is explained in plain English and translated into terms a drilling, completions, or production engineer already knows, exactly when the code in front of you needs it, never before.

Strong operational experience and comfort in Excel are more useful starting points here than prior coding experience.

<br>
&nbsp;

## Hardware Requirements

Every chapter in Part I and most of Part II runs on an ordinary laptop CPU — no GPU required. The embedding model used from Chapter 4 onward (`all-MiniLM-L6-v2`) and the vector index in Chapter 8 (`faiss-cpu`) are both deliberately chosen to be small and fast on CPU. Chapter 5's `llm_call` argument is provider-agnostic: plug in a local model or a hosted API, and your hardware needs follow whichever you choose.

<br>
&nbsp;

## Companion Pipeline

[**DDR_UTAH_FORGE**](https://github.com/djimrastephane/DDR_UTAH_FORGE) is a separate, public repository: a real, working DDR intelligence pipeline built specifically against this book's public archive, which Part II's chapters reference for verified real-world numbers (a real 2,943-chunk global index, a real detected reporting gap, and so on). This book's own code never depends on it — every chapter's script in `book/code/chapter_NN/` runs standalone against the committed sample archive. See [Appendix A, Section 3](https://djimrastephane.github.io/ddr-rag-book/appendix/appendix_a_environment_setup.html#the-companion-pipeline-for-part-ii) for how to clone it and how the two projects relate.

<br>
&nbsp;

## Exercises

Every chapter includes a **Practical exercise** (a guided, checkable task using the real sample archive) and a **Challenge exercise** (a harder, more open-ended extension). Reference solutions for challenge exercises live alongside each chapter's code, e.g. [`book/code/chapter_01/challenge/`](book/code/chapter_01/challenge).

<br>
&nbsp;

## Bonus Material

Every chapter ends with a **Repository files** table listing the exact files — in this repository and, for Part II, in the companion pipeline — that back everything the chapter claims. A few worth knowing about on their own:

- [`book/code/chapter_01/build_sample_archive.py`](book/code/chapter_01/build_sample_archive.py) and [`book/code/chapter_08/build_full_archive.py`](book/code/chapter_08/build_full_archive.py) reproduce this book's curated 10-report and full 76-report Utah FORGE archives from the public source.
- Each chapter's **Field notes** callout is a real, independently-verified result checked against the actual archive before being written down — not an illustrative estimate.
- [`book/appendix/appendix_b_oilfield_glossary.qmd`](book/appendix/appendix_b_oilfield_glossary.qmd) extends Chapter 2's abbreviation dictionary with common oilfield terms beyond what this specific archive contains.

<br>
&nbsp;

## Questions, Feedback, and Contributing to This Repository

Questions, corrections (an oilfield abbreviation that's wrong for your basin, a chapter that assumes something it shouldn't, a bug in the code), and feedback are all welcome via [GitHub Issues](https://github.com/djimrastephane/ddr-rag-book/issues).

<br>
&nbsp;

## Citation

If you find this book or its code useful for your work, please consider citing it.

Chicago-style citation:

> Djimra, Stephane. *Building Industrial RAG Systems from Daily Drilling Reports*. 2026. https://github.com/djimrastephane/ddr-rag-book.

BibTeX entry:

```bibtex
@book{ddr-rag-book,
  author  = {Djimra Stephane Soulanoudjingar},
  title   = {Building Industrial RAG Systems from Daily Drilling Reports},
  year    = {2026},
  url     = {https://djimrastephane.github.io/ddr-rag-book/},
  github  = {https://github.com/djimrastephane/ddr-rag-book}
}
```
