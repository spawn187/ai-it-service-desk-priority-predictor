# Exchange Online mail-flow triage

## Scope and keywords
Exchange Online, email delivery, message trace, transport rule, quarantine, NDR, levélkézbesítés, e-mail nem érkezik meg.

## Safe diagnostic steps
- Confirm sender, recipient, UTC send time, message subject pattern, and whether an NDR was generated.
- Capture the message ID and review Message Trace with an approved read-only role.
- Check Microsoft 365 service health, quarantine state, connector health, and recent transport-rule changes.
- Compare internal-to-internal, outbound, and inbound delivery paths to narrow the affected boundary.
- Document whether the issue affects one mailbox, one domain, or multiple organizations.

## Escalation criteria
Escalate suspected data loss, broad mail-flow interruption, compromised connectors, or malicious forwarding to the service owner and security team.

## Prohibited autonomous actions
Do not release quarantined content, change transport rules, alter connectors, or disable anti-phishing controls automatically.
