"""Chapter 7 challenge solution: a minimal segment-aware splitter.

Treats any all-caps line under 6 words as a section heading and starts a
new segment there, so a chunk doesn't blend casing-table content with
mud-table content with time-breakdown narrative.

Usage:
    python code/chapter_07/challenge/segment_aware_chunking.py datasets/ddr_text/FORGE-16A-78-32_Drilling_038_2020-11-26.txt
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

HEADING_PATTERN = re.compile(r"^[A-Z][A-Z0-9 ,/&()\-]{2,}$")


@dataclass
class Segment:
    title: str
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def is_heading(line: str) -> bool:
    """A line counts as a section heading if it's short (<= 6 words) and
    entirely uppercase letters/digits/punctuation -- the pattern every
    real section header in this archive (MUD, BHA, TIME BREAKDOWN, ...)
    happens to follow, and no data row does (verified in Chapter 7's own
    Field Notes)."""
    words = line.split()
    return bool(words) and len(words) <= 6 and bool(HEADING_PATTERN.match(line))


def segment_aware_split(text: str) -> list[Segment]:
    """Walk the report line by line, starting a new Segment every time a
    heading line is found. Everything between one heading and the next
    (inclusive of the heading itself) becomes that segment's content --
    so a chunk boundary lines up with a real section boundary instead of
    an arbitrary token count."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    segments: list[Segment] = []
    current = Segment(title="(preamble)", lines=[])

    for line in lines:
        if is_heading(line):
            # Close out the segment we were building and start a fresh one.
            if current.lines:
                segments.append(current)
            current = Segment(title=line, lines=[])
        current.lines.append(line)
    if current.lines:
        segments.append(current)
    return segments


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "datasets/ddr_text/FORGE-16A-78-32_Drilling_038_2020-11-26.txt")
    text = path.read_text(encoding="utf-8")
    segments = segment_aware_split(text)

    print(f"{path.name}: {len(segments)} segments\n")
    for seg in segments:
        print(f"--- {seg.title} ({len(seg.lines)} lines) ---")

    section_titles = {"CASING", "MUD", "DRILL BITS", "PUMPS", "BHA",
                       "SURVEY DATA", "TIME BREAKDOWN", "CONSUMABLES", "BOP"}
    found = {seg.title for seg in segments} & section_titles
    print(f"\nFound {len(found)} of this report's real section headers as "
          f"segment boundaries: {sorted(found)}")
