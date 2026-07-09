from __future__ import annotations

import sys

from common import REQUIRED_FIELDS, load_markdown, load_taxonomy, markdown_files, repo_root


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def validate_file(path, taxonomy):
    metadata, body = load_markdown(path)
    errors = []

    if not metadata:
        errors.append("missing YAML frontmatter")
        return errors

    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"missing required field: {field}")

    domain = metadata.get("domain")
    category = metadata.get("category")
    subcategory = metadata.get("subcategory")
    difficulty = metadata.get("difficulty")
    content_type = metadata.get("content_type")
    audience = as_list(metadata.get("audience"))

    domains = taxonomy.get("domains", {})
    domain_data = domains.get(domain)
    if not domain_data:
        errors.append(f"invalid domain: {domain}")
    else:
        categories = domain_data.get("categories", {})
        if category not in categories:
            errors.append(f"invalid category for {domain}: {category}")
        elif subcategory not in categories[category]:
            errors.append(f"invalid subcategory for {domain}/{category}: {subcategory}")

        if difficulty not in domain_data.get("allowed_difficulty", []):
            errors.append(f"invalid difficulty for {domain}: {difficulty}")

        allowed_audience = set(domain_data.get("allowed_audience", []))
        for item in audience:
            if item not in allowed_audience:
                errors.append(f"invalid audience for {domain}: {item}")

        if content_type not in domain_data.get("allowed_content_types", []):
            errors.append(f"invalid content_type for {domain}: {content_type}")

    if not body.strip():
        errors.append("empty article body")

    return errors


def main() -> int:
    root = repo_root()
    taxonomy = load_taxonomy()
    files = markdown_files()
    failures = {}

    for path in files:
        errors = validate_file(path, taxonomy)
        if errors:
            failures[path] = errors

    print(f"Scanned {len(files)} Markdown files under {root / 'knowledge'}")

    if failures:
        print("\nMetadata validation failed:")
        for path, errors in failures.items():
            rel = path.relative_to(root)
            print(f"\n- {rel}")
            for error in errors:
                print(f"  - {error}")
        return 1

    print("Metadata validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

