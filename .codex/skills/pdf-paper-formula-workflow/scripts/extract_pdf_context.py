#!/usr/bin/env python3
"""
Extract page-local text windows or term-centered snippets from a PDF.

Designed for formula-recovery workflows on native-text technical PDFs.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


def parse_pages(spec: str, page_count: int) -> list[int]:
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            if start > end:
                start, end = end, start
            for page in range(start, end + 1):
                if 1 <= page <= page_count:
                    pages.add(page - 1)
        else:
            page = int(part)
            if 1 <= page <= page_count:
                pages.add(page - 1)
    return sorted(pages)


def normalize(text: str) -> str:
    return text.replace("\x00", "").strip()


def collect_pages(reader: PdfReader, page_indexes: list[int]) -> list[dict[str, str | int]]:
    results = []
    for idx in page_indexes:
        text = normalize(reader.pages[idx].extract_text() or "")
        results.append({"page": idx + 1, "text": text})
    return results


def collect_terms(reader: PdfReader, terms: list[str], context_chars: int) -> list[dict[str, str | int]]:
    results = []
    for page_idx, page in enumerate(reader.pages):
        text = normalize(page.extract_text() or "")
        if not text:
            continue
        for term in terms:
            for match in re.finditer(re.escape(term), text, flags=re.IGNORECASE):
                start = max(0, match.start() - context_chars)
                end = min(len(text), match.end() + context_chars)
                results.append(
                    {
                        "page": page_idx + 1,
                        "term": term,
                        "start": match.start(),
                        "end": match.end(),
                        "snippet": text[start:end],
                    }
                )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text context from a PDF.")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--pages", help="1-based page list/ranges, e.g. 7-9,12")
    parser.add_argument("--term", action="append", default=[], help="Search term; repeatable")
    parser.add_argument("--context-chars", type=int, default=1000, help="Context around term hits")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of plain text")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader = PdfReader(str(pdf_path))

    output: dict[str, object] = {
        "pdf": str(pdf_path),
        "page_count": len(reader.pages),
    }

    if args.pages:
        page_indexes = parse_pages(args.pages, len(reader.pages))
        output["pages"] = collect_pages(reader, page_indexes)

    if args.term:
        output["matches"] = collect_terms(reader, args.term, args.context_chars)

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"PDF: {pdf_path}")
    print(f"Pages: {len(reader.pages)}")

    for item in output.get("pages", []):
        print(f"\n===== PAGE {item['page']} =====\n")
        print(item["text"])

    for item in output.get("matches", []):
        print(f"\n===== MATCH page={item['page']} term={item['term']} =====\n")
        print(item["snippet"])


if __name__ == "__main__":
    main()
