# Network and site outage triage

## Scope and keywords
Network outage, site unreachable, WAN, LAN, DNS, DHCP, VPN, packet loss, warehouse connectivity, hálózati kiesés, telephely nem elérhető.

## Safe diagnostic steps
- Confirm the affected sites, user count, business services, start time, and whether monitoring shows a common failure point.
- Check approved monitoring dashboards for WAN, DNS, DHCP, VPN, firewall, and core-switch health.
- Capture packet-loss, latency, interface, and routing evidence without changing production configuration.
- Compare the incident with provider notices, maintenance windows, and recent network changes.
- Validate whether an approved alternate path or business-continuity workaround is available.

## Escalation criteria
Activate major-incident review for mission-critical site outages, multi-site impact, safety implications, or loss of warehouse and logistics processing.

## Prohibited autonomous actions
Do not reboot network infrastructure, change routes, modify firewall policy, or fail over production links without an authorized change path.
