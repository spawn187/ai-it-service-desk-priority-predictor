# Intune and endpoint compliance triage

## Scope and keywords
Microsoft Intune, endpoint compliance, device configuration, enrollment, Autopilot, Defender, noncompliant device, eszköz megfelelőség.

## Safe diagnostic steps
- Confirm device ID, operating-system version, enrollment state, last check-in time, and assigned user.
- Review Intune device compliance details and policy assignment using read-only access.
- Compare the failing control with a known-compliant device from the same deployment ring.
- Capture Company Portal, MDM, and relevant Windows event-log errors before remediation.
- Check whether a recent policy, application, certificate, or enrollment-profile change aligns with the failure time.

## Escalation criteria
Escalate widespread noncompliance, Defender alerts, certificate failures, or an Autopilot deployment-ring regression.

## Prohibited autonomous actions
Do not wipe, retire, isolate, re-enroll, or remove a device from management without verified ownership and explicit approval.
