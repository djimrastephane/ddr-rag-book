# Changelog

All notable changes to this book are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This book does not use Semantic Versioning in the strict software sense;
version numbers mark reader-facing milestones (major content additions,
structural changes, or corrections), not API compatibility.

## [Unreleased]

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
