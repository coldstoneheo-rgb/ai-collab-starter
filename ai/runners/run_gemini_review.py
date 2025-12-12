#!/usr/bin/env python3
# Placeholder Gemini runner
import os
from pathlib import Path
from ai.context7.rag_pipeline import fetch_top_k

def send_to_gemini(prompt, api_key):
    print("=== GEMINI REQUEST ===")
    print(prompt[:1000])
    return "# UI/UX OK\n- No issues detected."

def main():
    tpl = Path('.github/AI_PROMPTS/gemini_uiux.txt').read_text()
    docs = fetch_top_k("ui", k=5)
    prompt = tpl + "\n\nContext:\n" + "\n".join([d['path'] for d in docs])
    resp = send_to_gemini(prompt, os.getenv('GEMINI_API_KEY',''))
    print(resp)

if __name__ == '__main__':
    main()
