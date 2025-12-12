
---

## `docs/AI_COLLAB_GUIDE.md`
```markdown
# AI Collab Starter — Guide

This document explains how to use the ai-collab-starter template.

## Overview
This template wires up:
- .github workflows for PR-time AI reviews
- AI prompt templates (.github/AI_PROMPTS/)
- Local RAG indexer (ai/context7/)
- Runner scripts (ai/runners/) which you must adapt to actual API clients

## 1) Install & Initialize
- Linux/macOS:
  ```bash
  ./scripts/init_project.sh
