from __future__ import annotations

import json
import re

from common import load_markdown, markdown_files, repo_root, slugify


HEADING_RE = re.compile(r"^(#{2,6})\s+(.+)$", re.MULTILINE)


def as_list(value):
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def split_sections(body: str):
    matches = list(HEADING_RE.finditer(body))
    if not matches:
        return [("body", body.strip())] if body.strip() else []

    chunks = []
    intro = body[: matches[0].start()].strip()
    intro_payload = "`n".join(line for line in intro.splitlines() if not line.lstrip().startswith("#")).strip()
    if intro_payload:
        chunks.append(("intro", intro))

    for index, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        text = body[start:end].strip()
        if text:
            chunks.append((title, text))
    return chunks


def main() -> int:
    root = repo_root()
    output_path = root / "exports" / "jsonl" / "chunks.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for path in markdown_files():
        metadata, body = load_markdown(path)
        document_id = metadata.get("id", path.stem)
        for index, (section_title, text) in enumerate(split_sections(body), start=1):
            records.append(
                {
                    "chunk_id": f"{document_id}::{index:03d}-{slugify(section_title)}",
                    "document_id": document_id,
                    "title": metadata.get("title", ""),
                    "domain": metadata.get("domain", ""),
                    "category": metadata.get("category", ""),
                    "subcategory": metadata.get("subcategory", ""),
                    "content_type": metadata.get("content_type", ""),
                    "keywords": as_list(metadata.get("keywords")),
                    "related": as_list(metadata.get("related")),
                    "source_path": path.relative_to(root).as_posix(),
                    "text": text,
                }
            )

    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} chunks to {output_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


