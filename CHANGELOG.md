# Changelog

## 0.9.0
- Portable grounding: added **reflex 9 — persist design intent + reasoning, per project** (every project keeps a DECISIONS.md + a status snapshot; read at kickoff, record each locked decision when made).
- New **SRX / firewall skill family** (7 skills) vendored from JNPRAutomate/fw-skills-share (MIT, commit 798f3ed): parsing-srx-configs, srx-nat, srx-policy, srx-advpn, srx-autovpn-full-tunnel, srx-ipsec-hub-spoke, srx-chassis-cluster-proxmox. A separate, read/plan-first family from the guardrails; provenance in ATTRIBUTION-fw-skills-share.md. Upstream device-touching deploy skills intentionally excluded.

## 0.8.0
- Coexistence: SETUP + connector-setup now state the plugin registers no MCP automatically, and how to avoid name/tool collisions with connectors a colleague already runs.
- Guardrails refresh: added the *convenient-fact trap* (verify the fact that would make your theory click, don't assert it); a *confirm-the-service-survived-the-change* gate (success returned != daemon still running); and *frame the requirement, not a solution* at kickoff.
- New: chat-segmentation (hub-and-spoke) methodology — `grounding/CHAT-SEGMENTATION.md` + `reference-designs/templates/effort-registry.md`.

