# Changelog

## 0.12.0
- **New guardrail reflex — "check the shelf before you build or improvise."** Before writing a runbook, procedure, or skill for a vendor platform, list what the connectors already ship (`skills_list` → `skills_load`) and read it. Build only for the DELTA; name the vendor skill in yours and state the handoff; when both cover a step, theirs wins. Added as reflex 9 in `eo-guardrails`, reflex 10 in the portable grounding, and folded into the toolset-awareness section and the pre-flight self-check.
- Origin: an AOS 8 → AOS 10 migration skill was built here without first checking that the connector already bundles a 192KB `aos-migration` skill. They turned out to be complements (assessment+planning vs execution+triage) — but that was luck, not method.

## 0.11.0
- New skill **aos8-to-aos10-central-migration** — the controller-managed AOS 8 campus AP → AOS 10 / New Central migration runbook: cluster-type fork (hybrid vs pure New Central), the four prerequisite gates (GreenLake claim + valid subscription, persona, group, site), creating the AOS 10 group via Classic `configuration/v3/groups` so the device-collection actually populates, the controller-side `ap convert` sequence, the three things that leave a converted AP silent (site, WLAN disabled-by-default, the `no <field>` push rejections), the scope/precedence model, RADIUS/802.1X gotchas, and the green verification signature.
- Includes the corrections that superseded earlier conclusions from the same effort: the firmware-floor theory, "dmo needs TAC", "site scope is broken", and "AP firmware upgrade is Select-Availability gated" were all disproved.

## 0.10.0
- New skill **aos10-gateway-tunnel-build** — HPE Aruba AOS 10 Mobility Gateway + tunnel-mode WLAN: the system-IP-must-be-a-VLAN gate (loopback silently breaks AP tunnel anchoring), the New Central onboarding/prerequisite order, the Classic local-override Reset Config step, cluster/bucket-map facts, create-only forwarding mode, and the healthy-tunnel verification signature. Includes the correction that `show ap active` is NOT the done-test on AOS 10.
- Skills are now inventoried by the practice's drift check, so a skill that contradicts the canonical lessons record surfaces as drift instead of rotting.

## 0.9.0
- Portable grounding: added **reflex 9 — persist design intent + reasoning, per project** (every project keeps a DECISIONS.md + a status snapshot; read at kickoff, record each locked decision when made).
- New **SRX / firewall skill family** (7 skills) vendored from JNPRAutomate/fw-skills-share (MIT, commit 798f3ed): parsing-srx-configs, srx-nat, srx-policy, srx-advpn, srx-autovpn-full-tunnel, srx-ipsec-hub-spoke, srx-chassis-cluster-proxmox. A separate, read/plan-first family from the guardrails; provenance in ATTRIBUTION-fw-skills-share.md. Upstream device-touching deploy skills intentionally excluded.

## 0.8.0
- Coexistence: SETUP + connector-setup now state the plugin registers no MCP automatically, and how to avoid name/tool collisions with connectors a colleague already runs.
- Guardrails refresh: added the *convenient-fact trap* (verify the fact that would make your theory click, don't assert it); a *confirm-the-service-survived-the-change* gate (success returned != daemon still running); and *frame the requirement, not a solution* at kickoff.
- New: chat-segmentation (hub-and-spoke) methodology — `grounding/CHAT-SEGMENTATION.md` + `reference-designs/templates/effort-registry.md`.

