# Historical weak baseline — not used in the application

```text
You are an experienced IT support specialist.
Read the ticket below, decide its priority, and recommend the best next steps.
Be helpful and concise.

Ticket:
{ticket_text}
```

## Why it was rejected

- mixes instructions and untrusted ticket data;
- has no grounding source or citation contract;
- has no structured output schema;
- does not separate facts, assumptions, and missing information;
- has no human-review or least-agency rule;
- can imply that actions were executed;
- has no sensitive-data handling;
- has no direct or indirect injection control;
- cannot be regression-tested reliably;
- duplicates priority classification that is better handled by the classical ML layer.

The file is retained only to make prompt evolution inspectable.
