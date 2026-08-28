# Changelog

## 0.17.0
- **aos10-gateway-tunnel-build §5d: root cause established.** A tunnel-mode (overlay) SSID cannot use the AP's UNDERLAY VLAN - it is rejected at the AP (`a2g-sta-up` -> ~100ms -> `a2g-sta-down`, `TUNNEL_DOWN`, ~1 Hz SSID flap). `show ap debug vlan` (VLAN Assignment Failure Table) names the reason in one line: 17 failures on the underlay VLAN, zero after moving to a dedicated client VLAN. Also records what was NOT the fix, and flags an unexplained difference in 802.1X behaviour on the underlay VLAN.

## 0.16.0
- Guardrail: **put the condition IN the artifact that travels.** Prerequisites stated only in the surrounding conversation are lost the moment a block is pasted onward. Re-read the artifact alone before handing it over.

## 0.15.0
- Guardrail: **name the ACTOR for every proposed action.** Handing over a paste-ready block without saying who runs it silently makes it the Human's job. Check the recipient can actually execute it first - a test needing a physical client, a Human-only credential, or a write on a system another session drives cannot be run by them, and saying so is part of the proposal.

## 0.14.0
- **eo-guardrails: four new always-on reflexes and three change gates**, distilled from a long live engagement where each one was paid for in lost hours. These are behavioural, so they ship in the always-on grounding skill rather than a task-triggered skill - a rule that only loads when a task matches will not fire at the moment you need it.
  - *Diagnose by READING, not by changing* - the error names an object on the device; cloud/controller reads return that system's intent and cannot show state it does not know about. Countable test: changed the management system twice without a fresh device reading = poking, not diagnosing.
  - *Suspect your instrument before the world* - a uniformly negative OR uniformly positive result is a claim about your tooling first; a null/error means "wrong call", never "capability does not exist".
  - *Validate the success criterion before you chase it.*
  - *Inherited claims are hypotheses* - handoffs, audits, prior sessions.
  - *An intention is not a record* - write it the same turn, read it back; a cited-but-uncommitted baseline is not a backout path.
  - *Prove a new check FIRES before trusting its silence* - plus a control that must NOT fire.
  - *Capability is not permission* - read the terms and robots.txt in full before ingesting anyone's content; identify honestly, and if an honest client is refused, you are refused.

## 0.13.0
- Guardrail: **skills are a distribution channel - serialise the writes.** Spoke/engagement chats propose skill edits; the coordinator lands, versions and pushes. Prompted by two chats committing to the same SKILL.md three minutes apart. Explicitly not a quality gate on spokes: their contributions that day were sound and one corrected a coordinator error.
- Corollary recorded: writing something into a skill does not make it operative - a skill not loaded mid-session is not consulted.

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

