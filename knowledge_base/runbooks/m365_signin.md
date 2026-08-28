# Microsoft 365 and Entra ID sign-in triage

## Scope and keywords
Identity, authentication, Entra ID, Microsoft 365, MFA, Conditional Access, sign-in failure, bejelentkezési hiba, többtényezős hitelesítés.

## Safe diagnostic steps
- Confirm whether the impact is limited to one user, one location, or the entire tenant.
- Capture the UTC timestamp, application name, correlation ID, and exact sign-in error.
- Review Entra sign-in logs and Conditional Access results using an approved read-only role.
- Check Microsoft 365 service health and compare the event with recent identity changes.
- Validate device time, network reachability, and whether the issue reproduces in a clean browser session.

## Escalation criteria
Escalate immediately when privileged accounts, widespread lockout, suspicious sign-ins, or a tenant-wide authentication outage is suspected.

## Prohibited autonomous actions
Do not disable MFA, weaken Conditional Access, reset privileged credentials, or modify identity policy without explicit approval and audit logging.
