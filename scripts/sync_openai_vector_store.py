"""Sync the knowledge base into an OpenAI vector store for the website assistant.

Full re-sync: finds (or creates) a vector store by name, removes its existing
files, and uploads every markdown article under knowledge/. Idempotent — safe
to run on every push to main.

Requires: pip install openai
Env vars:
  OPENAI_API_KEY        (required)
  VECTOR_STORE_NAME     (optional, default: bougie-bams-knowledge-base)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
STORE_NAME = os.environ.get("VECTOR_STORE_NAME", "bougie-bams-knowledge-base")


def main() -> int:
    client = OpenAI()

    # 1. Find or create the vector store
    store = None
    for vs in client.vector_stores.list(limit=100):
        if vs.name == STORE_NAME:
            store = vs
            break
    if store is None:
        store = client.vector_stores.create(name=STORE_NAME)
        print(f"Created vector store: {store.id}")
    else:
        print(f"Found vector store: {store.id}")

    # 2. Remove existing files (and delete the underlying file objects)
    removed = 0
    for vs_file in client.vector_stores.files.list(vector_store_id=store.id, limit=100):
        client.vector_stores.files.delete(vector_store_id=store.id, file_id=vs_file.id)
        try:
            client.files.delete(vs_file.id)
        except Exception:
            pass  # file object may already be gone
        removed += 1
    print(f"Removed {removed} old files")

    # 3. Upload all knowledge articles
    paths = sorted(KNOWLEDGE.rglob("*.md"))
    if not paths:
        print("No markdown files found under knowledge/ — aborting")
        return 1

    streams = [open(p, "rb") for p in paths]
    try:
        batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=store.id, files=streams
        )
    finally:
        for s in streams:
            s.close()

    print(f"Uploaded {len(paths)} files — batch status: {batch.status}")
    print(f"VECTOR_STORE_ID={store.id}")
    return 0 if batch.status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
