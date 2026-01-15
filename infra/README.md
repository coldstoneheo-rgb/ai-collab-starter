# Infrastructure

This directory contains infrastructure configuration and deployment scripts.

## Purpose

Infrastructure code in this directory is considered **sensitive** and requires:
- Enterprise mode review (all AI agents)
- Human approval before merge
- Extra scrutiny for security and compliance

## Contents

- Deployment configurations
- Infrastructure as Code (IaC) templates
- CI/CD pipeline definitions
- Environment setup scripts

## Sensitive Path Detection Test

This file modification is used to test the router's sensitive path detection feature.
Expected behavior:
- Router detects `infra/` prefix
- Mode escalates to `enterprise`
- All agents (Claude, Gemini, Perplexity) are enabled
- `autofix_allowed` is set to `false`
