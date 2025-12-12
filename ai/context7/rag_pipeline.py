# simple RAG helper that loads the index and returns top-k documents (local)
import json
from typing import List

def load_index(path='ai/context7/index.json'):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_top_k(query: str, k=5, index_path='ai/context7/index.json'):
    docs = load_index(index_path)
    # naive scoring by substring matches (placeholder — replace with vector search)
    scored = []
    q = query.lower()
    for d in docs:
        score = d.get('content','').lower().count(q)
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s,d in scored[:k] if s>0]
