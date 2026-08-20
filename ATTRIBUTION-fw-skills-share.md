# Vendored: SRX / firewall skill family

The 7 skills listed below are vendored (copied unmodified) from the community project
**JNPRAutomate/fw-skills-share** — https://github.com/JNPRAutomate/fw-skills-share
Upstream commit `798f3ed` (2026-08-19). License: **MIT** (© 2026 fwskillsshare contributors).

Vendored:
- `parsing-srx-configs`
- `srx-nat`
- `srx-policy`
- `srx-advpn`
- `srx-autovpn-full-tunnel`
- `srx-ipsec-hub-spoke`
- `srx-chassis-cluster-proxmox`

These form a **separate family** from the Engineering Office governance/runbook skills — Juniper
SRX design/config/audit/troubleshoot playbooks. They are **read/plan-first by design**: any change
to a device requires explicit approval and post-change verification. Each retains its upstream
frontmatter (author, license) and self-contained references.

The device-touching upstream **deploy** skills (`clearpass-proxmox-deploy`, `sd-onprem-proxmox-deploy`)
are intentionally **not** vendored here — they are lab-ops, not colleague-shareable guidance.

Upstream is MIT-licensed and so is this repository; no upstream text was modified.
