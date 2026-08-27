---
name: aos10-gateway-tunnel-build
description: Build, change, or troubleshoot an HPE Aruba AOS 10 Mobility Gateway and a tunnel-mode WLAN in
  New Central. Use for gateway system-IP / controller-ip work, gateway onboarding after ZTP, gateway
  clusters and bucket maps, AP-to-gateway tunnel anchoring, or when a tunnel-mode SSID will not anchor
  clients. Trigger words: AOS 10 gateway, Mobility Gateway, controller-ip, system IP, tunnel mode WLAN,
  tunnel orchestrator, OTO, ipsec-map, bucket map, Isoleader, cluster member IP, VLAN 4094, local
  override, Reset Config, show ap active, SM_STATE_CONNECTING, overlay-wlan, Primary Gateway Cluster,
  gw-cluster-list, dtunnel, WLAN will not anchor, gateway has no virtual-AP, RADIUS sourced from the AP.
---

# AOS 10 Mobility Gateway + tunnel-mode WLAN — build and verify

Hard-won runbook. Every gate below was paid for with a real outage or a wrong conclusion.
Follow the order. Do not improvise.

---

## 0. Ground yourself in the RIGHT doc set — first, always

**Check the URL contains `techdocs/new-central/`.** The Classic Central pages
(`techdocs/central/.../aos10x/cfg/aps/gw-cfg-aos10.htm`, "Provisioning Gateways", Gateway Pools) open
with *"Classic Central offers the following options"* and scope Gateway Pools to *SD-WAN* gateways. They
do **not** apply to New-Central-managed devices. Reading the wrong doc set will send you down dead ends.

Key pages:
- Onboarding: `new-central/content/get-started/onboard-gws.htm`
- Tunnel orchestrator: `aos/aos10/services/oto/`
- Cluster formation / planning: `aos/aos10/design/gw-clusters/formation/` and `/planning/`

**Read the SETUP doc before diagnosing a device you did not build.** The onboarding doc explains where
VLAN 4094 comes from, what auto-import does, and names the remedy for a stuck device. Skipping it costs
hours.

---

## 1. The single most important fact

**On an AOS 10 campus Mobility Gateway the System IP MUST be a VLAN interface — never a loopback.**

A loopback has no linktag, so the datapath cannot resolve a VLAN for the tunnel-termination IP and the
IPsec map is never packed. Everything the API and the orchestrator report stays green while the tunnel
is dead.

Fault signature (`show log errorlog` on the gateway):
```
ipopulate_vlan_from_linktag 558 IPv4 VLAN is not learnt from FPAPPS configured ip <loopback-ip>
pack error
fpapps procIkeIpsecMsg: Unable to find the ipsec map for ap-ipsecmap-<ap-mac> ... TUN_DOWN
dim handle_device_reg_msg: No device entry found for <ap-mac>
```
Corroborating symptoms:
- `show crypto-local ipsec-map` -> `Sos Program: Ingress: Yes Egress: NO`, `Peer gateway: 0.0.0.0`, `Interface: VLAN 0`
- `show datapath ipsec-map` -> 0 entries
- `show crypto oto` -> `BG-SRC Err SPI/Map/Vlan/B-Mesh` with the **Vlan** column climbing
- AP `show ata endpoint` -> `HBT(.../Sent/Rcv)` with **Rcv 0**, state `SM_STATE_CONNECTING`

If `show controller-ip` says *"configured to be loopback interface"*, that IS the fault. Stop tuning
cluster / WLAN / OTO config.

**Do NOT diagnose from `show crypto isakmp sa`.** Per the OTO doc, AOS 10 skips IKE phase 1/2 entirely —
the orchestrator generates the SPIs and keys. `% No active ISAKMP SA` and the CPSEC / mode-config
counters in `show crypto isakmp stats` are EXPECTED, not the fault.

---

## 1b. The SECOND most important fact — a tunnel-mode WLAN needs a gateway-cluster BINDING

A WLAN can sit at `forward-mode: FORWARD_MODE_L2` (that IS tunnel — the enum has only
`FORWARD_MODE_BRIDGE` and `FORWARD_MODE_L2`) with an **empty Primary Gateway Cluster** and **no
`overlay-wlan` object at any scope**. Nothing warns you. The WLAN looks correct in every listing and on
the air, and no client will ever anchor.

**The binding lives in a separate object**, not in the WLAN profile:

```
central_get_overlay_wlan(view_type=LOCAL, scope_id=<site>, device_function=CAMPUS_AP)
-> {} ............ NO BINDING. This is the fault.

healthy:
{"profile": "<SSID>", "overlay-profile-type": "WIRELESS_PROFILE", "essid-name": "<SSID>",
 "gw-cluster-list": [{"cluster": "<cluster-name>", "cluster-redundancy-type": "PRIMARY",
                      "cluster-scope-id": "<site-scope-id>", "cluster-type": "CLUSTER_ID",
                      "tunnel-type": "GRE"}]}
```

### Fault signature — memorise this, it is nothing like the §1 signature
The tunnel infrastructure is **completely healthy** and everything in §6 passes. What you see instead:

- gateway `show wlan virtual-ap` -> `Virtual AP profile "default" undefined.`
- gateway `show wlan ssid-profile` -> `SSID Profile "default" undefined.`
- gateway `show aaa profile` -> **no AAA profile for the SSID** (a healthy one appears automatically,
  named `<SSID>_<digits>_`)
- gateway RADIUS counters (`show aaa authentication-server radius statistics`) **never move** during a
  client attempt
- Central client events show `Client 802.1x Radius Reject` / `Client EAP Failure` — and ClearPass logs the
  request **sourced from the AP's IP**, not the gateway's system IP

That last point is the tell, and it is easy to misread: **the AP falls back to terminating 802.1X itself.**
If your RADIUS server sees requests from the AP address while the gateway's own counters stay at zero, the
SSID is not anchored, no matter what the WLAN profile says.

### Fixing it — the binding is CREATE-ONLY and the API is unusable
`central_manage_overlay_wlan action=create` returns **HTTP 500** on a payload the parser accepts (the
`PRIMARY` enum validates), at every scope and object_type. PATCH returns "profile doesn't exist". The
undocumented required sub-fields (`cluster-scope-id`, `cluster-type`, `tunnel-type`) are why.

**Do it in the Central UI Create WLAN flow** (see §8 — Traffic Forwarding Mode and Primary Gateway Cluster
are disabled on an existing WLAN, so the WLAN must be deleted and recreated). Capture the full profile
JSON first.

---

## 2. Build order (New Central) — prerequisites BEFORE anything destructive

Per the onboarding doc, create these first. Skipping any of them can strand the gateway.

1. **VLAN profile** — Enable L3, and give it a **static IP**.
   *A VLAN only appears in the Gateway System "IPv4 System IP VLAN" drop-down once it has a static IP.*
   An empty drop-down means "no VLAN interface has a static IP", NOT a platform limitation.
   Also set **IPv6 Address Assignment = DHCP** — it defaults to Static-with-empty-address, which commits
   `ipv6 address static` with no address, is invalid, and puts the device into Config Rollback.
2. **Gateway System profile** — System IP VLAN = the VLAN above. **No loopback.**
3. **Static Routing profile** — default gateway via **Device-Specific Parameters > Gateway/AOS-S
   Parameters > Default Gateways**. The generic *IP Routes* row does NOT render on a gateway.
4. **DNS Server profile** — mandatory. Without a resolver the gateway cannot resolve the conductor FQDN.
5. **User Administration profile** — carries `mgmt-user admin`. It lives in the auto-imported config and
   is wiped by a reset.

Only then do anything that resets or re-syncs the device.

---

## 3. When Central "cannot" change the gateway's uplink or system IP

Look for a **Classic Central LOCAL OVERRIDE**. This is not a hybrid-cluster limitation — the New Central
onboarding doc names it as a REQUIRED onboarding step:

> "Onboarding gateways requires an additional step of clicking **Reset Config** in the
> **Configuration Audit > Local Overrides** page in Classic Central WebUI."

Path: Classic Central toggle (top right) > Devices > **Gateways** > the device > left-nav **Device** >
**Config Audit** tab > *Manage local overrides* > select the row > **Reset config**.

The override typically contains exactly the things you could not change from New Central:
`controller-ip loopback`, `interface loopback <ip>`, `vlan 4094`, `switchport access vlan 4094`,
`hostname`, `country`, `mgmt-server`, cp-bandwidth-contracts.

**Reset Config wipes device-specific config and reloads the device.** That is why §2 must be done first.

Do NOT author configuration in Classic. Classic is used only for this removal action.

---

## 4. What is device-owned vs Central-managed

- All ZTP ports land in **VLAN 4094**; the ZTP uplink is a DHCP client there. This is normal.
- Onboarding **auto-imports** the device's connectivity config into **device-scope profiles**
  (VLAN, L3 VLAN, Static Routing, GW Interface Configuration, User Administration, DNS, System Info).
  If those objects are missing from Central but present on the device, the auto-import did not complete —
  that is the anomaly to chase, not "Central can't model it".
- An **ACP-managed gateway refuses BOTH `configure terminal` AND exec `write`**
  ("This controller is managed by an ACP"). Budget for *no CLI at all* before planning any device-level fix.
- SSH is still useful for `show` commands. But **`show running-config` over plain ssh returns EMPTY**
  (it needs a pty) — use the Central show-command API. Never conclude a config line is absent from an
  empty ssh result.

---

## 5. VERIFY EVERY WRITE ON THE DEVICE — an API 200 is not proof

This is the single most repeated mistake. `SUCC_001` / HTTP 200 means Central accepted the object. It
does **not** mean the device rendered it.

- After a WLAN change: confirm on the AP with `show ap bss-table` (the BSS should disappear/reappear, and
  the `tot-t` uptime column should reset). A continuous uptime means your change never landed.
- After a gateway change: `show switches` (Config ID should advance, state `UPDATE SUCCESSFUL`) and
  `show configuration failure` (Total Failures must be 0).
- Use **CLI Viewer > Candidate Config** at device scope to see the exact CLI Central intends to push, and
  diff it against the device's running config.

**Write to the scope where the object is actually assigned.** Updating the *library* copy of a WLAN does
nothing to the device. Find the real assignment in the profile list's **"Assigned Device Scope"** column
or the profile's **References** tab.

**Never infer assignment from a scoped GET** — a scoped GET returns the library/effective view and will
happily show an object at every scope_id. Confirm in the UI.

**Config Rollback with Total Failures 0 is a commit-confirm TIMEOUT, not a bad config.** Read
`show configuration failure` first: >0 means a command was genuinely rejected (fix the config); 0 means
nothing was rejected — look in `show log errorlog` for `cfgm_rollback_timeout` / `cfgm_rollback_is_bad_config`,
which is the device auto-reverting because the ACP web-socket did not re-establish inside the rollback window.

---

## 6. Verification signature of a HEALTHY tunnel

Gateway:
```
show controller-ip                -> "configured to be vlan interface: N"   (NOT loopback)
show crypto-local ipsec-map       -> Peer gateway: <ap-ip>, Interface: VLAN N,
                                     Key Valid: Yes, Sos Program: Ingress: Yes Egress: Yes,
                                     Boot-Strap State: Done
show datapath ipsec-map           -> >= 1 entry
show crypto ipsec sa              -> Total IPSEC SAs >= 1
show datapath tunnel              -> Current Entries (AP GRE) >= 1
show crypto oto                   -> Channel state CONNECTED, BG-SRC Err .../Vlan/... = 0
show lc-cluster group-membership  -> Cluster Enabled, self <system-ip>
```
AP:
```
show ata endpoint                 -> IP ADDR = gateway system IP, STATE SM_STATE_CONNECTED,
                                     HBT Rcv non-zero, Missed 0
show ap debug stm-bucketmap       -> UAC = gateway system IP, and the bucket maps are NON-ZERO
```
Central UI: Devices > Gateways > **Clusters** > cluster > Summary (VLAN Mismatch: No), Gateways (node Up),
Tunnels (Status Up).

### The success test is NOT `show ap active`
In AOS 10 the gateway does not manage APs ("AP management and control is no longer provided by
Gateways"). `show ap active`, `show ap database` **and `show ap bss-table` run ON THE GATEWAY** are AOS 8
heritage commands and may legitimately read **Num APs: 0** on a perfectly healthy AOS 10 gateway **with a
live tunnelled client on it**. Do not use them as the done-test. (Note the asymmetry with §5:
`show ap bss-table` is still the right check when run ON THE AP to confirm a WLAN change landed.)

A confirmed real-world reading: `show ap bss-table` on the gateway reported `Num APs: 0 / Num
Associations: 0` at the same moment `show user-table` showed a fully authenticated tunnelled client.

**The real test:** a tunnelled client appears in the gateway's `show user-table` and
`show datapath station table`, and Clients Active > 0 on the cluster dashboard. If a client associates and
gets service but never appears there, it is being **bridged at the AP**, not tunnelled.

What success actually looks like — the `Forward mode` column is the proof:
```
show user-table
IP <ip>  MAC <client-mac>  Name <user>  Role <role>  Auth 802.1x
Essid/Bssid  <SSID>/<ap-mac>   Profile <SSID>_<digits>_   Forward mode: dtunnel
User Entries: 1/1

show datapath station table   -> <client-mac>  TunId <id>  VLAN <n>
RADIUS statistics             -> Raw Rq >0, Chal >0, Acc >=1, Bad Auth 0
```
`dtunnel` = decrypt-tunnel = the client is tunnelled to the gateway. `Forward mode` reading anything else
(or the client never appearing) means bridged at the AP.

### Probing RADIUS without a client — a REJECT is the SUCCESS signal
`aaa test-server pap <server-name> <user> <deliberately-wrong-password>` from the gateway exercises
transport, shared secret, NAS-client entry and source IP in one shot, with no wireless client needed.
AOS prints `Authentication failed` for BOTH a reject and a timeout, so read the counters, not the text:
- `Rej` increments with `Bad Auth 0` / `Mismatch Rsp 0` -> **PASS**. The server received, decrypted and
  processed it: secret correct, NAS client defined, source IP as expected.
- `Tmout` with no response -> FAIL: wrong secret, undefined NAS client, or unreachable.

**Ignore the first packet's latency.** A newly created auth-server routinely shows `AvgRspTm` ~5000 ms on
its very first request (cold socket setup) and trips the 5 s timeout, then settles to single-digit ms.
Read `ExpAuthTm` (moving average), not the cumulative `AvgRspTm`, and do not open a ClearPass performance
investigation on the strength of one cold packet.

---

## 7. Cluster facts worth knowing before you touch one

- A cluster **can consist of one or several gateways** — a single-node cluster is valid.
- Central reports a lone node's role as **"Isoleader"** and treats it as normal, not an error.
- Clusters are normally created **automatically at the group or the site level**. A manual cluster at
  site-collection scope is permitted by the config model but is not the documented shape — call the
  deviation out.
- **The cluster member IP MUST equal the gateway's system IP.** A mismatch gives
  "self-ip X not present ... cluster disabled". Restarting the device does NOT fix a member-IP mismatch.
- The **bucket map published by the cluster leader** assigns each client's UDG. An all-zero bucket map
  means no client will ever anchor, even with the tunnel up.
- A gateway MAC belongs to exactly one cluster; emptying `ipv4-gateways` does not release it — the old
  cluster profile must be deleted.

---

## 8. Create-only fields

**Traffic Forwarding Mode (Bridge/Tunnel/Mixed) and Primary Gateway Cluster are editable ONLY in the
Create WLAN flow.** On an existing WLAN they are disabled at every scope. You cannot convert a bridge
SSID to tunnel — you must recreate it. Budget for that before proposing a cluster change.

Capture the full existing WLAN profile JSON before deleting anything.

---

## 9. Working with an inherited handoff

Treat prior handoff/state documents as **claims to verify, not facts**. A real example: a handoff asserted
"the gateway has no VLAN 1", "no ISAKMP SA means the AP isn't forming IPsec", and "the scratch SSID was
removed". All three were wrong, and each sent a session down a dead end. Re-verify the current state on
the device before acting on any inherited assertion — then correct the handoff.

Corollary: **validate the success criterion itself** before spending hours driving it. Confirm from the
vendor doc that the metric indicates the thing you want (see §6 — `show ap active` does not).

---

## 9b. Recreating a WLAN in the UI — scope and field traps

Recreating a WLAN to restore a create-only field is routine (§8). These will bite you during it:

- **"Create as a local profile" is a create-time decision.** Leave it unticked and you get a SHARED
  (library) profile. A SHARED WLAN **cannot reference a site-LOCAL server group** —
  `Cannot find in library '<name>' of type 'aruba-auth-server-group' referred in '<ssid>' of type
  'aruba-wlan'`. If the WLAN you are replacing was site-local and pointed at site-local AAA objects, tick
  the box; otherwise you must also promote the AAA objects to the library, which breaks the
  "lab override dies at the site boundary" pattern.
- **The Primary Server drop-down lists only library/shared auth servers.** Site-local ones do not appear,
  even at that site's own scope. Use the inline **New Authentication Server** link.
- **WPA2-Enterprise (and WPA-Enterprise, Both, Dynamic WEP) are greyed out** until you **uncheck the 6 GHz
  band AND Wi-Fi 7 (802.11be)**. The banner says so — "Disable 6 GHz Band, Wi-Fi 7 (802.11be) to enable
  legacy key management methods" — but it is easy to read as a hint rather than a hard gate. A WLAN
  restored to a WPA2-Enterprise baseline must have its bands set first.
- **Auth Server Mode must be "RADIUS with CoA"** if the design needs Change-of-Authorization. The UI then
  warns: *CoA requires Dynamic Authorisation to be enabled in the Authentication Server Global profile* —
  a separate object. Setting the server mode alone does not give you working CoA.
- **A healthy push is observable.** After the binding lands, the gateway grows an AAA profile named
  `<SSID>_<digits>_` (with `802.1X Authentication Profile`, default role and a `..._auth_svg` server group)
  and `show switches` Config ID advances. If Config ID moves but no AAA profile appears, the binding did
  not take.

---

## 10. Recovery

If the gateway loses its path to Central (no DNS, bad uplink) and the CLI is ACP-locked, it may need a
**power cycle** — Central-side config is not persisted to flash by the device, so it can come back on the
last-saved config. If that fails, factory reset via the LCD front panel or console. Both need hands on the
box, so make sure §2 is complete before you create that situation.

---

## Provenance

Built from a live AOS 10 gateway + tunnel-mode WLAN engagement (2026-08-27). Sections 5 and 9 restate
universal Engineering Office gates at the point of use; the canonical statements live in the guardrails
(`eo-guardrails`) and in the practice's LESSONS record. If they ever disagree, the canonical record wins —
fix this file.

**Revised 2026-08-27 (same day, second pass) after tunnel mode was PROVEN end to end.** Added §1b
(the gateway-cluster / `overlay-wlan` binding), §9b (UI scope and field traps when recreating a WLAN), the
`dtunnel` success evidence and the `aaa test-server` probe technique in §6.

The first pass of this runbook was correct about §1 (loopback System IP) but silent on the second fault,
and that gap cost a full session: with the loopback already fixed, a tunnel-mode WLAN that had NO gateway
cluster bound presented as "the tunnel orchestrator does not work in this hybrid tenant" — which was
written into an engagement DECISIONS.md as a platform limitation and went unchallenged for two days. It
was not a platform limitation. §6 previously implied `show ap bss-table` was a valid gateway-side check;
on the gateway it reads `Num APs: 0` even with a live tunnelled client, which is exactly the false signal
that produced the wrong conclusion. That line is now corrected.

Standing lesson this file exists to prevent: **if every documented prerequisite reads green and the
product still does not work, suspect your own setup — not the product — and never commit "X cannot be
done" to a design record without a named mechanism and an explicit re-test trigger.**
