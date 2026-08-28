# Windows 365 Cloud PC connectivity triage

## Scope and keywords
Windows 365, Cloud PC, remote desktop, provisioning, connection failure, Frontline, cloud PC nem csatlakozik, távoli asztal.

## Safe diagnostic steps
- Confirm the Cloud PC status, provisioning state, assigned license, user identity, and last successful connection.
- Capture the client error, UTC timestamp, correlation ID, and connection method.
- Review Windows 365 service health, provisioning policy status, and Intune device record using read-only access.
- Compare browser and Remote Desktop client behavior and validate local network prerequisites.
- Check whether the failure began after a licensing, Conditional Access, network, image, or provisioning change.

## Escalation criteria
Escalate repeated provisioning failures, multi-user service impact, image defects, or suspected identity and network policy conflicts.

## Prohibited autonomous actions
Do not reprovision, resize, restore, deallocate, or delete a Cloud PC without approved change and data-protection checks.
