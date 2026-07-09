from __future__ import annotations

from common import load_markdown, markdown_files, repo_root


def as_csv(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value or "")


def main() -> int:
    root = repo_root()
    output_path = root / "exports" / "markdown" / "index.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for path in markdown_files():
        metadata, _ = load_markdown(path)
        rows.append(
            {
                "id": metadata.get("id", ""),
                "title": metadata.get("title", ""),
                "domain": metadata.get("domain", ""),
                "category": metadata.get("category", ""),
                "path": path.relative_to(root).as_posix(),
                "keywords": as_csv(metadata.get("keywords", [])),
                "related": as_csv(metadata.get("related", [])),
            }
        )

    lines = [
        "# Knowledge Base Index",
        "",
        f"Generated documents: {len(rows)}",
        "",
        "| ID | Title | Domain | Category | Path | Keywords | Related |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in sorted(rows, key=lambda item: item["id"]):
        lines.append(
            "| {id} | {title} | {domain} | {category} | {path} | {keywords} | {related} |".format(**row)
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

