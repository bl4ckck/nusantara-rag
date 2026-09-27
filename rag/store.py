import json

import chromadb

from .settings import get

COLLECTION = "nusantaracare"
CHUNKS = "data/chunks.json"


def collection():
    return chromadb.HttpClient(
        host=get("CHROMA_HOST"),
        port=int(get("CHROMA_PORT")),
    ).get_or_create_collection(COLLECTION)


def seed():
    col = collection()
    chunks = json.load(open(CHUNKS, encoding="utf-8"))
    if col.count() == len(chunks):
        return {"seeded": 0, "chunks": len(chunks)}
    try:
        col.delete(ids=[c["chunk_id"] for c in chunks])
    except Exception:
        pass
    # ponytail: full re-seed per corpus change; add version check when >1 doc
    col.add(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c.get("teks", c.get("text", "")) for c in chunks],
        metadatas=[{
            "doc_id": c.get("doc_id", "NC-OPS-001"),
            "section_title": c.get("section_title", ""),
            "doc_version": c.get("doc_version", "2.0"),
            "is_active": c.get("is_active", True),
        } for c in chunks],
    )
    return {"seeded": len(chunks), "chunks": len(chunks)}
