"""Convert plain document ids in '## Related Documents' sections to Obsidian wikilinks.

Builds an id -> filename map from frontmatter across knowledge/, then rewrites
lines like '- some-doc-id' to '- [[file-stem|some-doc-id]]'. Idempotent.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"

id_re = re.compile(r"^id:\s*(\S+)", re.M)

# Build id -> stem map
id_map = {}
for path in KNOWLEDGE.rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    m = id_re.search(text)
    if m:
        id_map[m.group(1)] = path.stem

changed = 0
for path in KNOWLEDGE.rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    in_related = False
    out = []
    modified = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_related = stripped == "## Related Documents"
        elif in_related and stripped.startswith("- ") and "[[" not in stripped:
            doc_id = stripped[2:].strip()
            if doc_id in id_map:
                indent = line[: len(line) - len(line.lstrip())]
                nl = "\n" if line.endswith("\n") else ""
                line = f"{indent}- [[{id_map[doc_id]}|{doc_id}]]{nl}"
                modified = True
        out.append(line)
    if modified:
        path.write_text("".join(out), encoding="utf-8")
        changed += 1

print(f"Mapped {len(id_map)} ids; updated {changed} files.")
