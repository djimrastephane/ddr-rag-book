# Changelog

All notable changes to this book are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This book does not use Semantic Versioning in the strict software sense;
version numbers mark reader-facing milestones (major content additions,
structural changes, or corrections), not API compatibility.

## [Unreleased]

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
