# Bougie Bams Knowledge Base

The Bougie Bams Knowledge Base is a structured Markdown repository for Mahjong education, product support, event operations, teaching material, FAQs, and future AI assistant workflows.

This repository is documentation-first. It is designed to stay readable for people while also being easy to validate, index, and convert into retrieval chunks for vector search.

## How This Supports AI Agents

Each knowledge article uses YAML frontmatter with consistent metadata. The scripts in `scripts/` can validate required fields, build a Markdown index, and split articles into retrieval-friendly JSONL chunks.

Future assistants can use these chunks to answer questions about Bougie Bams, Mahjong lessons, product guidance, events, and support workflows without sending the full knowledge base in every prompt.

## Folder Structure

- `knowledge/mahjong/` contains game education, rules explanations, strategy, etiquette, teaching material, FAQs, and decision trees.
- `knowledge/products/` is reserved for product support content.
- `knowledge/events/` is reserved for classes, open play, tournaments, retreats, and hosting content.
- `knowledge/company/` is reserved for mission, policy, shipping, returns, and company FAQs.
- `knowledge/media/` is reserved for blog, YouTube, and newsletter content.
- `knowledge/operations/` is reserved for internal admin, instructor, and support documentation.
- `knowledge/glossary/` contains short retrieval-friendly term entries.
- `templates/` contains authoring templates.
- `exports/` contains generated indexes and chunk files.

## Authoring Rules

- Keep one topic per file.
- Preserve all YAML frontmatter fields.
- Use short sections with clear headings.
- Prefer original explanations, examples, and teaching notes.
- Add related document ids when a reader should continue elsewhere.
- Keep examples general and do not include annual NMJL card hands.
- Use stable document ids that match the folder and topic.

## Copyright Limitations

Do not copy, reproduce, or closely paraphrase official NMJL copyrighted rulebook text or annual card content. Do not include specific annual card hands. When official interpretation is required, direct players to consult the current official NMJL card or rulebook.

## Add A New Article

1. Copy the closest template from `templates/`.
2. Save the new file under the most specific `knowledge/` folder.
3. Fill every frontmatter field from `metadata-schema.yaml`.
4. Add short sections with practical, original content.
5. Add related document ids and vector tags.
6. Run validation and regenerate exports.

## Validation And Chunk Generation

From the repository root:

```bash
python scripts/validate_metadata.py
python scripts/generate_index.py
python scripts/chunk_markdown.py
```

Generated files are written to:

- `exports/markdown/index.md`
- `exports/jsonl/chunks.jsonl`

