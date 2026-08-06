---
name: nac-guest-coa
description: Stand up or validate guest onboarding with Change-of-Authorization (CoA) on a Mist + Aruba
  ClearPass NAC, using the Juniper-native Disconnect (Terminate-Session) path on udp/3799 — the Cisco-free
  approach for all-Juniper APs. Use whenever guest captive-portal role change, CoA / Dynamic
  Authorization, 802.1X/MAC-auth guest flow, or ClearPass+Mist interop is designed, deployed, or debugged.
  Trigger words: CoA, Change of Authorization, guest onboarding, captive portal role change,
  Disconnect-Request, udp/3799, Terminate Session, ClearPass, Mist guest WLAN, Dynamic Authorization.
---

# nac-guest-coa

> Design / deploy / validate guest onboarding CoA on Mist + ClearPass using the **Juniper-native
> Disconnect** path (ClearPass Reauthenticate is Cisco/Tellabs-only). **Change-making + interop — fully
> gated.** **Self-contained:** the design below is complete on its own; if your `standards_source` has a
> matching reference design, follow it as authoritative. Uses your Mist + ClearPass connectors. Governing:
> [[eo-guardrails]] — Human-Authority approval for customer writes, secrets out-of-band, validate-to-the-
> wire, verify the observed effect not doc-conformance. Baseline first with [[config-backup]]; any Mist
> template change via [[mist-template-rollout]].

## The core design decision (don't relitigate)

ClearPass's built-in **Reauthenticate-Session** exists only for **Cisco/Tellabs**. Juniper/Aruba/HPE have
**Terminate/Disconnect** + Bounce-Port only. So the all-Juniper guest flow uses a **Disconnect-Request
(RADIUS code 40)** on **udp/3799**: the client briefly re-associates and re-auths into the post-
registration role. Avoids registering a Juniper AP under a Cisco vendor profile. Trade-off: a short guest
re-associate, acceptable for a role change.

## Auth + CoA flow (the acceptance target)

1. Guest associates → Mist AP MAC-auth (Access-Request, guest SSID in `Called-Station-Id`) → ClearPass.
2. ClearPass → Access-Accept, **pre-auth captive-portal role** (redirect, no internet).
3. Guest self-registers + logs in on the ClearPass captive portal (WEBAUTH service).
4. `[Guest]` enforcement rule fires **`[Juniper Terminate Session]`** → ClearPass sends **Disconnect-
   Request (code 40)** to the AP on **udp/3799**.
5. AP drops the session; client re-associates + re-auths.
6. ClearPass returns the **post-registration role** (full access).

## Guardrails carried from the standard

- **Never write a customer org/ClearPass without Human-Authority approval.** Read-only until approved;
  baseline first ([[config-backup]] — Mist access-assurance + ClearPass policy/enforcement).
- **Secrets out-of-band only.** RADIUS shared secret (must match on the Mist WLAN and the ClearPass Network
  Device) from your `credentials_file`; presence, never value.
- **Reference by ID/variable, not literal.** On Mist, the ClearPass RADIUS server is a **site/org
  variable**, not a literal IP (Site-Setting `vars` — see [[mist-template-rollout]]).
- **Validate to the wire.** "Configured" is not "working" — acceptance is the packet.

## Key configuration (adapt values, keep the shape)

**ClearPass — Network Device (the Mist AP):** IP = AP NAS IP; RADIUS shared secret; **Vendor = Juniper**;
`coa_capable = true`, `coa_port = 3799`.

**ClearPass — enforcement profile `[Juniper Terminate Session]`** (type RADIUS_DynAuthZ), returning:
`Calling-Station-Id = %{Radius:IETF:Calling-Station-Id}` and `Acct-Session-Id =
%{Radius:IETF:Acct-Session-Id}`. Wire into the WEBAUTH enforcement policy `[Guest]` rule after the
MAC-caching profile. **Prerequisites: Insight enabled; RADIUS Message-Authenticator retained.**

**Mist — guest WLAN:** RADIUS auth (udp/1812) + acct (udp/1813) to the ClearPass variable; **enable CoA /
Dynamic Authorization** so the AP accepts inbound CoA on udp/3799; shared secret matches ClearPass.

**Ports:** AP→ClearPass udp/1812–1813 (auth/acct); ClearPass→AP **udp/3799** (CoA Disconnect).

## Validate (to the wire — the definition of done)

1. Capture baseline first ([[config-backup]]).
2. Drive a guest login while watching for CoA on udp/3799 (a synthetic session + listener if you have one).
3. **Acceptance:** a **Disconnect-Request (code 40) observed on udp/3799**; the guest transitions to the
   post-registration role; **Insight** shows the session. Doc-conformance alone is not acceptance.
4. If no code 40: check the AP is registered **Vendor = Juniper** with `coa_port=3799`, the WLAN has Dynamic
   Authorization enabled, shared secrets match on both ends, Message-Authenticator retained, Insight enabled.

## Do NOT

- Do not register a Juniper AP under a Cisco vendor profile to get Reauthenticate — use Disconnect.
- Do not hardcode the RADIUS secret or the ClearPass IP — secret out-of-band, IP as a Mist variable.
- Do not declare success from config read-back — require the observed code-40 on the wire.
- Do not write a customer org/ClearPass without Human-Authority approval and a baseline + revert path.
