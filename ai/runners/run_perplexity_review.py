#!/usr/bin/env python3
# Placeholder Perplexity runner
from pathlib import Path
from ai.context7.rag_pipeline import fetch_top_k

def send_to_perplexity(prompt, api_key):
    print("=== PERPLEXITY REQUEST ===")
    print(prompt[:1000])
    return "# Compliance: No immediate risk found."

def main():
    tpl = Path('.github/AI_PROMPTS/perplexity_compliance.txt').read_text()
    docs = fetch_top_k("compliance", k=5)
    prompt = tpl + "\n\nContext:" + "\n".join([d['path'] for d in docs])
    resp = send_to_perplexity(prompt, "")
    print(resp)

if __name__ == '__main__':
    main()
