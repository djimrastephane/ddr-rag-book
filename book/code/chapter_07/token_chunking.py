"""Chapter 7: token-based chunking with overlap.

Usage:
    python code/chapter_07/token_chunking.py datasets/ddr_text/FORGE-16A-78-32_Drilling_038_2020-11-26.txt
"""

import re
import sys
from pathlib import Path

import tiktoken

PAGE_MARKER = re.compile(r"--- Page (\d+) ---\n?")


def chunk_text_by_tokens(text: str, chunk_tokens: int = 60,
                          overlap_tokens: int = 15) -> list[str]:
    """Slide a fixed-size window across the token stream, moving forward
    by (chunk_tokens - overlap_tokens) each step.

    cl100k_base is the same tokenizer OpenAI's GPT models use -- tokens
    are sub-word pieces, not whole words, so encode()/decode() round-trip
    the text through its token IDs. The overlap means the last
    `overlap_tokens` of one chunk are repeated at the start of the next,
    so a sentence that would otherwise be cut exactly at a chunk boundary
    has a chance to appear whole in at least one chunk.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text.strip())
    chunks, start = [], 0
    while start < len(tokens):
        end = min(len(tokens), start + chunk_tokens)
        chunks.append(enc.decode(tokens[start:end]).strip())
        if end == len(tokens):
            break
        start = max(0, end - overlap_tokens)
    return chunks


def split_pages(pages_text: str) -> list[tuple[int, str]]:
    """Undo Chapter 1's "--- Page N ---" markers: split extracted text
    back into (page_number, page_text) pairs.

    Chunking runs per page, not on the whole joined document, so a chunk
    can never straddle a page boundary -- the only way a chunk's page
    number can stay unambiguous once it's chunked further below.
    """
    matches = list(PAGE_MARKER.finditer(pages_text))
    pages = []
    for i, match in enumerate(matches):
        page_number = int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(pages_text)
        pages.append((page_number, pages_text[start:end].strip()))
    return pages


def chunk_pages_by_tokens(pages_text: str, chunk_tokens: int = 60,
                           overlap_tokens: int = 15) -> list[tuple[int, str]]:
    """Chapter 7's real gap, closed: chunk_text_by_tokens() above returns
    plain strings with no memory of which page they came from, so nothing
    downstream (Chapter 8's index, Chapter 10's Citation) can cite a page
    number without it. This does the same token-window chunking, per
    page, and returns each chunk paired with its real page number.
    """
    chunks_with_pages = []
    for page_number, page_text in split_pages(pages_text):
        for chunk in chunk_text_by_tokens(page_text, chunk_tokens, overlap_tokens):
            chunks_with_pages.append((page_number, chunk))
    return chunks_with_pages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python token_chunking.py <path-to-text-file>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    chunks_with_pages = chunk_pages_by_tokens(text, chunk_tokens=60, overlap_tokens=15)

    print(f"{path.name}: {len(chunks_with_pages)} chunks\n")
    for i, (page_number, chunk) in enumerate(chunks_with_pages, start=1):
        print(f"--- Chunk {i} (page {page_number}) ---")
        print(chunk)
        print()
