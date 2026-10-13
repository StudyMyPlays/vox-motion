#!/usr/bin/env python3
"""Check a Vox narration script before any paid voice or clip generation.

The script file holds one entry per 10s block, written as ``Block N: text``
(the text may continue on following lines). Markdown headings, HTML comments
and code-fence markers are ignored.

Errors (exit 1): missing/out-of-order blocks, block count mismatch, digits
(numbers must be spelled out), stage directions in brackets/parentheses,
lines far outside the word budget.
Warnings: lines outside 20–24 words, estimated read time outside the
9.0–10.5s take window, greetings in the cold open.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

WORDS_TARGET = (20, 24)
WORDS_HARD = (14, 30)
TAKE_WINDOW = (9.0, 10.5)
# Flowing narration reads ~2.5 words/s; narrator voices add ~0.7s per
# sentence break. A rough model, good enough to flag the risky lines.
WORDS_PER_SEC = 2.5
SENTENCE_PAUSE_SEC = 0.7

BLOCK_RE = re.compile(r"^\s*(?:[#>*_\-\s]*)Block\s+(\d+)\s*\**\s*[:.\-—–]?\s*(.*)$", re.I)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
GREETINGS = ("in this video", "welcome", "hey guys", "hi everyone", "today we")


@dataclass
class Block:
    number: int
    text: str
    words: int = 0
    est_sec: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_blocks(source: str) -> list[Block]:
    source = COMMENT_RE.sub("", source)
    blocks: list[Block] = []
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("```"):
            continue
        match = BLOCK_RE.match(line)
        if match:
            blocks.append(Block(int(match.group(1)), match.group(2).strip()))
        elif line.startswith("#"):
            continue
        elif blocks:
            blocks[-1].text = f"{blocks[-1].text} {line}".strip()
    return blocks


def estimate_seconds(text: str) -> float:
    words = len(text.split())
    sentences = max(1, len(re.findall(r"[.!?]+(?=\s|$)", text)))
    return words / WORDS_PER_SEC + SENTENCE_PAUSE_SEC * (sentences - 1)


def check_block(block: Block, is_first: bool) -> None:
    text = block.text
    block.words = len(text.split())
    block.est_sec = round(estimate_seconds(text), 1)

    if not text:
        block.errors.append("empty block")
        return
    if re.search(r"\d", text):
        block.errors.append("contains digits; spell numbers out (\"seventy percent\")")
    if re.search(r"[\[\](){}<>]", text):
        block.errors.append("contains brackets/parentheses; narration must be plain spoken text")
    if not WORDS_HARD[0] <= block.words <= WORDS_HARD[1]:
        block.errors.append(f"{block.words} words; far outside the {WORDS_TARGET[0]}–{WORDS_TARGET[1]} budget")
    elif not WORDS_TARGET[0] <= block.words <= WORDS_TARGET[1]:
        block.warnings.append(f"{block.words} words; target {WORDS_TARGET[0]}–{WORDS_TARGET[1]}")
    if not TAKE_WINDOW[0] - 1.0 <= block.est_sec <= TAKE_WINDOW[1]:
        block.warnings.append(
            f"estimated {block.est_sec}s read; likely to miss the {TAKE_WINDOW[0]}–{TAKE_WINDOW[1]}s take window"
        )
    if is_first and any(g in text.lower() for g in GREETINGS):
        block.warnings.append("cold open contains a greeting; state the hook flat")


def check_script(source: str, expected_blocks: int | None = None) -> tuple[list[Block], list[str]]:
    blocks = parse_blocks(source)
    problems: list[str] = []
    if not blocks:
        problems.append("no 'Block N:' entries found")
        return blocks, problems
    numbers = [b.number for b in blocks]
    if numbers != list(range(1, len(blocks) + 1)):
        problems.append(f"blocks must be numbered 1..N in order, found {numbers}")
    if expected_blocks is not None and len(blocks) != expected_blocks:
        problems.append(f"expected {expected_blocks} blocks, found {len(blocks)}")
    for i, block in enumerate(blocks):
        check_block(block, is_first=i == 0)
    return blocks, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("script", type=Path, help="run/script.md")
    parser.add_argument("--blocks", type=int, help="expected block count N")
    parser.add_argument("--json", action="store_true", help="print a machine-readable report")
    args = parser.parse_args(argv)

    blocks, problems = check_script(args.script.read_text(encoding="utf-8"), args.blocks)
    error_count = len(problems) + sum(len(b.errors) for b in blocks)

    if args.json:
        print(json.dumps({
            "ok": error_count == 0,
            "problems": problems,
            "blocks": [b.__dict__ for b in blocks],
        }, indent=2))
    else:
        for b in blocks:
            status = "ERROR" if b.errors else ("warn" if b.warnings else "ok")
            print(f"Block {b.number:>2}  {b.words:>2} words  ~{b.est_sec:>4}s  {status}")
            for msg in b.errors:
                print(f"    error: {msg}")
            for msg in b.warnings:
                print(f"    warn:  {msg}")
        for msg in problems:
            print(f"error: {msg}")
        total = sum(b.est_sec for b in blocks)
        print(f"{len(blocks)} blocks, ~{total:.0f}s narration, {error_count} error(s)")
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
