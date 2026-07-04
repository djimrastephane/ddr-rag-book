"""Chapter 7: token-based chunking with overlap.

Usage:
    python code/chapter_07/token_chunking.py datasets/ddr_text/FORGE-16A-78-32_Drilling_038_2020-11-26.txt
"""

import sys
from pathlib import Path

import tiktoken


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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python token_chunking.py <path-to-text-file>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    chunks = chunk_text_by_tokens(text, chunk_tokens=60, overlap_tokens=15)

    print(f"{path.name}: {len(chunks)} chunks\n")
    for i, chunk in enumerate(chunks, start=1):
        print(f"--- Chunk {i} ---")
        print(chunk)
        print()
