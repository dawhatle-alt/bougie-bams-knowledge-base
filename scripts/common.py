from __future__ import annotations

import re
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "id",
    "title",
    "domain",
    "category",
    "subcategory",
    "difficulty",
    "audience",
    "content_type",
    "keywords",
    "related",
    "version",
    "last_updated",
    "source_type",
    "copyright_status",
]


FALLBACK_TAXONOMY: dict[str, Any] = {
    "domains": {
        "mahjong": {
            "categories": {
                "fundamentals": ["overview", "equipment", "tiles", "seating"],
                "rules": ["setup", "play", "calls", "jokers", "scoring", "endgame"],
                "strategy": ["beginner", "passing", "calling", "defense", "hand-selection"],
                "etiquette": ["casual-play", "communication", "hosting", "disputes"],
                "teaching": ["beginners", "lessons", "explanations"],
                "examples": ["practice", "scenarios"],
                "faq": ["rules", "beginner", "calls", "jokers"],
                "decision-trees": ["calls", "jokers", "strategy", "rules"],
                "glossary": ["terms"],
            },
            "allowed_difficulty": ["beginner", "intermediate", "advanced", "all"],
            "allowed_audience": ["players", "beginners", "instructors", "hosts", "customers", "support", "internal"],
            "allowed_content_types": ["article", "faq", "decision_tree", "glossary"],
        },
        "events": {
            "categories": {
                "classes": ["beginner", "intermediate", "private", "group"],
                "open-play": ["casual", "guided", "community"],
                "tournaments": ["registration", "rules", "scoring", "operations"],
                "retreats": ["planning", "schedule", "packing", "guest-experience"],
                "hosting": ["venue", "supplies", "checklists", "communication"],
            },
            "allowed_difficulty": ["beginner", "intermediate", "advanced", "all"],
            "allowed_audience": ["players", "beginners", "instructors", "hosts", "customers", "support", "internal"],
            "allowed_content_types": ["article", "faq", "decision_tree", "glossary", "checklist"],
        },
        "products": {
            "categories": {
                "tiles": ["materials", "care", "selection", "support"],
                "mats": ["care", "sizing", "selection", "support"],
                "racks": ["care", "selection", "support"],
                "bags": ["care", "sizing", "selection", "support"],
                "affiliate": ["recommendations", "disclosure", "support"],
            },
            "allowed_difficulty": ["beginner", "intermediate", "advanced", "all"],
            "allowed_audience": ["customers", "support", "internal", "players", "beginners"],
            "allowed_content_types": ["article", "faq", "decision_tree", "glossary", "product_note"],
        },
        "company": {
            "categories": {
                "mission": ["brand", "values", "story"],
                "policies": ["privacy", "terms", "conduct"],
                "shipping": ["timelines", "carriers", "tracking"],
                "returns": ["eligibility", "process", "exceptions"],
                "faq": ["general", "support", "orders"],
            },
            "allowed_difficulty": ["all"],
            "allowed_audience": ["customers", "support", "internal", "hosts"],
            "allowed_content_types": ["article", "faq", "decision_tree", "policy"],
        },
        "media": {
            "categories": {
                "blog": ["education", "events", "product", "community"],
                "youtube": ["lessons", "shorts", "product", "events"],
                "newsletters": ["announcements", "education", "promotions"],
            },
            "allowed_difficulty": ["beginner", "intermediate", "advanced", "all"],
            "allowed_audience": ["customers", "players", "beginners", "instructors", "internal"],
            "allowed_content_types": ["article", "faq", "glossary", "media_note"],
        },
        "operations": {
            "categories": {
                "admin": ["systems", "checklists", "reporting"],
                "instructors": ["lesson-plans", "standards", "materials"],
                "support": ["tickets", "refunds", "product-questions", "event-questions"],
            },
            "allowed_difficulty": ["all"],
            "allowed_audience": ["internal", "support", "instructors", "hosts"],
            "allowed_content_types": ["article", "faq", "decision_tree", "checklist", "procedure"],
        },
    }
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def markdown_files() -> list[Path]:
    return sorted((repo_root() / "knowledge").rglob("*.md"))


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",")]
    return value.strip("'\"")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    try:
        _, raw_meta, body = text.split("---", 2)
    except ValueError:
        return {}, text

    metadata: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in raw_meta.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and current_key:
            metadata.setdefault(current_key, [])
            if not isinstance(metadata[current_key], list):
                metadata[current_key] = []
            metadata[current_key].append(_parse_scalar(stripped[2:]))
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            metadata[key] = [] if value == "" else _parse_scalar(value)
    return metadata, body.lstrip()


def load_markdown(path: Path) -> tuple[dict[str, Any], str]:
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def load_taxonomy() -> dict[str, Any]:
    taxonomy_path = repo_root() / "taxonomy.yaml"
    try:
        import yaml  # type: ignore

        raw = yaml.safe_load(taxonomy_path.read_text(encoding="utf-8"))
        normalized = {"domains": {}}
        for domain, data in raw.get("domains", {}).items():
            categories = {}
            for category, category_data in data.get("categories", {}).items():
                categories[category] = category_data.get("subcategories", [])
            normalized["domains"][domain] = {
                "categories": categories,
                "allowed_difficulty": data.get("allowed_difficulty", []),
                "allowed_audience": data.get("allowed_audience", []),
                "allowed_content_types": data.get("allowed_content_types", []),
            }
        return normalized
    except Exception:
        return FALLBACK_TAXONOMY


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "chunk"

