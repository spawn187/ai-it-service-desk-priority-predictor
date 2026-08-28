# Prompt changelog

## 1.1.0 — 2026-08-28

- Added explicit direct and indirect prompt-injection boundaries.
- Required separation of facts, assumptions, and missing information.
- Restricted citations to application-provided evidence IDs.
- Made human approval and `automation_allowed=false` non-negotiable.
- Added prompt and input SHA-256 hashes for auditability.
- Added deterministic CI evaluation cases for PII, secrets, injection, grounding, and escalation.

## 1.0.0 — initial baseline

A basic role-and-task prompt produced useful text but lacked a strict output contract, context isolation, citation control, and regression tests. It is retained conceptually in the design documentation as the weak baseline, not as a production prompt.
