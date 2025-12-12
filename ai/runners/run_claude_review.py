#!/usr/bin/env python3
"""
Placeholder runner: loads PR diff and sends prompt to Claude API.
Replace `send_to_claude()` with real Claude API client call.
"""
import os, sys, json, argparse
from pathlib import Path
from ai.context7.rag_pipeline import fetch_top_k

def send_to_claude(prompt, api_key):
    # Placeholder: implement real HTTP call to Claude Code API
    print("=== CLAUDE REQUEST ===")
    print(prompt[:1000])
    return {"verdict":"APPROVE","issues":[],"tests":[]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr-number', type=int, default=None)
    args = parser.parse_args()
    # build context:
    top_docs = fetch_top_k("project overview", k=5)
    # load prompt template
    tpl = Path('.github/AI_PROMPTS/claude_review.txt').read_text()
    # build prompt (simple)
    prompt = tpl + "\n\nContext Docs:\n" + "\n\n".join([d['path'] for d in top_docs])
    api_key = os.getenv('CLAUDE_API_KEY','')
    resp = send_to_claude(prompt, api_key)
    print(json.dumps(resp, indent=2))

if __name__ == '__main__':
    main()
