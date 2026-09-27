import re

from . import llm, store

CITE = re.compile(r"\[(NC-OPS-001-C\d+)\]")
REFUSAL = llm.REFUSAL
TOP_K = 5


def answer(question):
    question = (question or "").strip()
    if not question:
        return {"jawaban": REFUSAL, "sitasi": []}
    try:
        res = store.collection().query(
            query_texts=[question], n_results=TOP_K, where={"is_active": True})
        ids, docs = res["ids"][0], res["documents"][0]
    except Exception:
        return {"jawaban": REFUSAL, "sitasi": [], "error": "retrieval unavailable"}
    if not ids:
        return {"jawaban": REFUSAL, "sitasi": []}
    try:
        raw = llm.complete(
            question, "\n\n".join(f"[{i}] {d[:1500]}" for i, d in zip(ids, docs)))
    except Exception:
        return {"jawaban": REFUSAL, "sitasi": [], "error": "answer generation failed"}
    cites = sorted(set(c for c in CITE.findall(raw) if c in set(ids)))
    if not cites:
        return {"jawaban": REFUSAL, "sitasi": []}
    return {"jawaban": raw, "sitasi": cites}
