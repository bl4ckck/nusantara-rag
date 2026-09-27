#!/usr/bin/env python3
"""Chunk SOP markdown -> data/chunks.json. One ## section = one chunk.
Oversized sections: LLM semantic split when configured, else paragraph split."""
import json
import os
import re
import urllib.request
from pathlib import Path

LIMIT = 3000
ARCHIVE = ("arsip", "v1.4", "nonaktif")


def load_dotenv(path=".env"):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def llm_split(text):
    base = os.environ["LLM_BASE_URL"].rstrip("/")
    body = json.dumps({
        "model": os.environ["LLM_MODEL"], "temperature": 0,
        "messages": [{"role": "user", "content":
            "Split text into chunks <=3000 chars at topic boundaries. "
            "Reply ONLY a JSON list of strings.\n\n" + text}],
    }).encode()
    req = urllib.request.Request(
        base + "/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {os.environ['LLM_API_KEY']}",
                 "User-Agent": "NusantaraCare-RAG/1.0",
                 "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.load(r)["choices"][0]["message"]["content"]
    return json.loads(re.search(r"\[.*\]", out, re.DOTALL).group(0))


def split_big(text):
    if os.getenv("LLM_API_KEY") and os.getenv("LLM_BASE_URL") and os.getenv("LLM_MODEL"):
        try:
            parts = [p for p in llm_split(text) if p.strip()]
            if parts:
                return parts
        except Exception as e:
            print("LLM split failed, paragraph fallback:", e)
    out, cur = [], ""
    for p in (x for x in text.split("\n\n") if x.strip()):
        if len(cur) + len(p) + 2 <= LIMIT:
            cur = (cur + "\n\n" + p).strip()
        else:
            out.append(cur)
            cur = p
    if cur:
        out.append(cur)
    return out


def main(src="nusantaracare_panduan_operasional_internal_v2.md", out="data/chunks.json"):
    text = Path(src).read_text(encoding="utf-8")
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    chunks = []
    for b in re.split(r"(?m)^(?=## )", text):
        b = b.strip()
        if len(b) < 200:
            continue
        m = re.match(r"## (.+)", b)
        title = m.group(1).strip() if m else "root"
        archived = any(x in title.lower() for x in ARCHIVE)
        parts = split_big(b) if len(b) > LIMIT else [b]
        for part in parts:
            chunks.append({
                "chunk_id": f"NC-OPS-001-C{len(chunks) + 1:03d}",
                "doc_id": "NC-OPS-001",
                "doc_version": "1.4" if archived else "2.0",
                "is_active": not archived,
                "section_title": title,
                "text": part,
            })
    assert chunks, "no chunks produced"
    assert any(not c["is_active"] for c in chunks), "v1.4 archive chunks missing"
    Path(out).parent.mkdir(exist_ok=True)
    json.dump(chunks, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(chunks)} chunks -> {out}")


if __name__ == "__main__":
    load_dotenv()
    main()
