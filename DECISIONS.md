# DECISIONS.md

## Why router-based dispatch?
To centralize decision-making and prevent:
- Cost explosion
- Workflow entanglement
- Uncontrolled AI execution

## Why fixed modes (lite/pro/enterprise)?
To avoid combinatorial complexity.
Behavior changes by mode, not by ad-hoc flags.

## Why no autofix merge?
Safety.
Early automation without trust metrics is unacceptable.

## Why RAG?
To constrain AI reasoning within project-specific context
and avoid generic or hallucinated recommendations.

## Why phased maturity?
Because full automation without guardrails
creates irreversible technical and organizational risk.

## Why strict governance?
Because AI failure modes scale faster than human failure modes.

## Why immutable logs?
Auditability and post-incident analysis are mandatory for trust.

## Why kill-switch?
Any autonomous system must be stoppable instantly.
