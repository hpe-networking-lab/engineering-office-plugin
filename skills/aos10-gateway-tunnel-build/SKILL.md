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

## 1c. `cluster-scope-id` — use the SITE, and never edit the binding in place

**Trap that takes an SSID off air with no in-place recovery.**

Aruba's own reference workflow (`central-python-workflows/tunneled-ssid-overlay`,
`wlan_overlay_profiles.yaml`) carries this comment:

```
# Change the cluster-scope-id to match your AP Device Group
```

**Following it broke a working SSID.** Setting `cluster-scope-id` to the AP **device group**
made `POC-COAONLINE` vanish from `show ap bss-table` entirely — the other four SSIDs on the
same AP were unaffected. Central renders the field red (it knows the value is invalid) but
**accepts the write anyway**.

Use the **SITE** scope id — the value a known-working tunnel SSID on the same cluster already
has. Verify against a working sibling before writing:

```
central_get_overlay_wlan(detailed=True)   # compare gw-cluster-list[].cluster-scope-id
```

### The binding is create-only in BOTH the API and the UI

§1b says the API is unusable for changing it. The UI is **also** locked, which is not obvious:

- **API update** fails with `Profile not found in library for
  aruba-aaa-captive-portal/sys_cnac_<ssid>` — updating `overlay-wlan` revalidates every
  referenced profile, and the Central NAC captive portal is a **system-generated** object that
  is not in the library view that path resolves against. A tunnel SSID with **no** captive
  portal updates fine; one **with** a portal cannot be updated at all.
- **UI**: Traffic Forwarding Mode and Primary/Secondary Gateway Cluster are greyed out at
  **both** site scope and Library scope. The control is a `DIV`, not a form input — the
  dropdown will not open and `form_input` is rejected.

### Repair: delete and recreate (the only route)

1. **Baseline everything first** — full WLAN profile, `overlay-wlan`, and every
   `config-assignment` naming the SSID.
2. `central_manage_overlay_wlan` delete, then `central_manage_wlan_profile` delete.
3. Recreate the WLAN as a **library object** (no `object_type` / `scope_id`).
4. Recreate `overlay-wlan` with the correct `cluster-scope-id`.
5. Re-assign **both** `wlan-ssids` and `overlay-wlan` to `CAMPUS_AP` at the site.

**The rebuild regenerates the gateway AAA profile with a NEW id**
(`<SSID>_<epoch>_`). Anything referencing the old id by name must be re-pointed.

### `out-of-service: TUNNEL_DOWN` is why a broken tunnel SSID "flaps"

A tunnel-mode WLAN carries `out-of-service: TUNNEL_DOWN`. When the tunnel cannot service the
SSID the AP pulls the VAP and retries, giving a ~1 Hz appear/vanish cycle in the client's
network list. **That flap is a symptom of tunnel unserviceability, not a fault in itself** —
do not debug the VAP; find out why the tunnel cannot carry that SSID's VLAN.

Distinguish it from a client-side problem with `show ap bss-table`: the `tot-t` column is the
BSS uptime. **If `tot-t` is large and unbroken, the SSID never went down** and what the user
sees is a client failing to associate, not a flapping VAP.

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

## 3b. Carrying a tagged client VLAN out of the gateway uplink

A tunnel-mode WLAN whose client VLAN never reaches the wire produces a VAP that **appears and vanishes
on a roughly 1 Hz cycle** — the SSID flaps in the client's list. That is the gateway taking the VAP out
of service because it cannot place clients on the VLAN. It is NOT a DHCP failure (a DHCP failure leaves
the SSID up with no address).

Three separate things must all be true. Missing any one gives the same flap:

1. **The VLAN must be assigned to the MOBILITY_GW persona**, not only CAMPUS_AP. A VLAN assigned to
   `CAMPUS_AP` at a site collection is invisible to the gateway. Check
   `central_get_config_assignments` for `profile-type: layer2-vlan` and the device-function column.
2. **The VLAN must be enabled.** Compare against VLAN 1's object: a working VLAN carries `"enable": true`.
   A VLAN created by assignment alone may have no enable flag at all.
3. **The uplink port must be a TRUNK.** This is the one most often waved away.

### The uplink VLAN mode is real, not cosmetic

Monitoring reporting `portType: Access, vlan: 1` means the port **untags everything** — it is not
"just showing the native VLAN". Per the VSG LAN-interface documentation:

> Access — "allow the LAN port to carry traffic only for the VLAN to which they are assigned. All
> transmitted and received traffic on the port is untagged."
> Trunk — "allow the LAN port to carry traffic for multiple VLANs... Native VLAN... Allowed VLAN"

An access-mode uplink is physically incapable of emitting a tagged client VLAN.

**Do NOT try to confirm this with the upstream switch MAC table in TUNNEL mode.** In tunnel mode client
traffic rides the GRE tunnel from the AP to the gateway, so the access switch never learns client MACs on
that VLAN from the AP port. `show mac-address-table vlan <id>` returning **"No MAC entries found"** is the
EXPECTED result and proves nothing — and with no client associated there is no frame in the network at
all. Treating that silence as a fault means debugging an empty network.

- **Bridge mode**: the switch MAC table IS a valid check — the AP tags client frames onto the wire itself.
- **Tunnel mode**: check the GATEWAY instead — `show datapath tunnel` (AP GRE entry count),
  `show user-table` (client entries), `show datapath vlan` (is the VLAN on the tunnel ports 2/0/x).

### The object and the field name

`ethernet-interfaces`, LOCAL at the gateway DEVICE scope. The trunk field is **`trunk-vlan-ranges`** —
there is no `allowed-vlans` node under `switchport`, and guessing that name produces a YANG parse error:

```json
"switchport":    {"interface-mode": "TRUNK", "native-vlan": 1, "trunk-vlan-ranges": ["1", "3115"]}
"trusted-vlans": ["1", "3115"]
```

Keep **native VLAN 1** so untagged management traffic is unaffected — the conversion is then a non-event
(verified: 0% packet loss across the change on both the gateway and the upstream 6300M).

**Learn the accepted payload shape on an UNUSED port first.** The gateway's other ports are typically
down and unused; write to one of those, read it back, then apply the proven shape to the live uplink.
The API validates server-side, so a wrong field name is rejected without reaching the device — but a
*valid but wrong* payload on the only uplink strands an ACP-locked box that has no CLI to recover it.

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

**`central_show_commands` parameter shape — the enum differs BETWEEN tools.** Getting it wrong returns
a 422 that is easy to read as "this doesn't work for APs" and to escalate to a human:

```
central_get_devices     device_type = ACCESS_POINT | SWITCH | GATEWAY     (upper, singular)
central_show_commands   device_type = aps | cx | aos-s | gateways         (lower, plural)
                        serial_number = <serial>      commands = "<one string>"   (NOT a list)
```
It works fine for APs. A chat concluded `central_show_commands` "returns null for APs", declared the AP
the one device it could not instrument, and asked the operator for credentials — the call shape was wrong.

**Tunnel mode: absence of client MACs on the client VLAN at the SWITCH is EXPECTED, not a fault.** Client
traffic rides the AP→gateway GRE tunnel; the access switch never sees client MACs on that VLAN from the
AP port. With no client associated there is nothing to see at all. Before diagnosing "zero frames on
VLAN n", confirm a client is actually associated (`show ap association` on the AP, `show user-table` on
the gateway) — otherwise you are debugging an empty network.

**And when a push FAILS, the error names a device object — go read the device first.** Central's
config-model reads return its own intent (library/effective view) and cannot show you state Central does
not know about, which is what a push failure usually is. Before changing anything in Central again:

```
show switches                                  # Config ID advancing? CONFIG FAILURE(n)?
show configuration failure                     # Total Failures 0 => commit-confirm timeout, not bad config
show running-config | include <object-in-the-error>
show aaa rfc-3576-server | show aaa server-group | show rights   # object lists
show aaa profile <name>                        # the profile that holds the reference
```

Worked example: `RFC 3576 Server "<ip>" is in use` on every push touching one WLAN, while Central showed
that server as `AUTH_ONLY` at every scope. Four read-only commands found the real cause — a DIFFERENT
SSID's AAA profile still carried the RFC-3576 reference, because its `primary-auth-server` drives
`rfc3576-server-list` while the other SSID used an `auth-server-group`. Every action taken against the
failing SSID was against the wrong object. **If you have changed Central more than once without a fresh
device reading, you are poking, not diagnosing.**

Note the AAA profile is `system created and non editable` — it is generated from the WLAN, and the
binding is STORED, not recomputed: forcing regeneration does not clear a stale entry. Repoint the source
field on the WLAN.


This is the single most repeated mistake. `SUCC_001` / HTTP 200 means Central accepted the object. It
does **not** mean the device rendered it.

- After a WLAN change: confirm on the AP with `show ap bss-table` (the BSS should disappear/reappear, and
  the `tot-t` uptime column should reset). A continuous uptime means your change never landed.
- After a gateway change: `show switches` (Config ID should advance, state `UPDATE SUCCESSFUL`) and
  `show configuration failure` (Total Failures must be 0).
- Use **CLI Viewer > Candidate Config** at device scope to see the exact CLI Central intends to push, and
  diff it against the device's running config.

**`central_get_*` can fail to return an object that EXISTS.** Verified 2026-08-28: a role created via
`central_manage_roles` (HTTP 200, `SUCC_001`) was absent from `central_get_roles` at site, collection,
global AND library scope — yet re-creating it returned
`Cannot create duplicate config, Module = Role where name='X' already exists in Library`. The write had
worked; the read was lying.

> **Existence probe that actually works: try to CREATE it again.** A duplicate-name error is proof the
> object exists. A clean create means it did not. This is an executable check — prefer it to a read-back
> whenever a config-model write "seems" to have vanished, and never conclude "the write silently failed"
> from a `get` alone. (Corollary: also check page size — a default 25-item page against 59 objects looks
> exactly like a missing object.)

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

## 5b. HOW to actually read an ACP-locked gateway — the mechanics S5 assumes

Section 5 tells you to read the device. This section exists because that repeatedly does not happen:
every obvious route returns empty or null, it looks like "no read access exists", and you fall back to
Central reads and start poking. **All three dead ends have answers.**

### The gateway SSH shell needs a PTY

Plain SSH to an AOS 10 gateway returns an EMPTY result. This has been mis-recorded as "SSH does not
work, use central_show_commands". Wrong on both halves. **Allocate a pty with `-tt` and it works:**

```bash
PW=$(cat /lab/.secrets/<gw-cred-file>)
sshpass -p "$PW" ssh -tt \
  -o StrictHostKeyChecking=no \
  -o KexAlgorithms=+diffie-hellman-group14-sha1 \
  -o HostKeyAlgorithms=+ssh-rsa \
  -o PubkeyAuthentication=no \
  admin@<gw-ip> "show switches"
```

An ACP-locked gateway refuses `configure terminal` and `write memory` — but **every `show` command
works.** Read-only is exactly what diagnosis needs. "ACP-locked" is not "unreadable".

### central_show_commands WORKS — but its device_type enum differs from every other tool

This is the single highest-value line in this section. `central_show_commands` returns `null` — not an
error — for every wrong argument, so a wrong enum value looks exactly like "unsupported device".

**The enums are NOT the same between tools:**

| Tool | `device_type` values |
|---|---|
| `central_get_devices` | `ACCESS_POINT` / `SWITCH` / `GATEWAY`  (UPPER, singular) |
| `central_show_commands` | `aps` / `cx` / `aos-s` / `gateways`  (lower, PLURAL) |

Also: the parameter is `serial_number` (not `serial`), and `commands` takes a **string**, not a list.

```python
central_show_commands(serial_number="<serial>", device_type="aps", commands="show ap bss-table")
```

Trying `ACCESS_POINT`, `AP`, `GATEWAY`, `MOBILITY_GW` all return `null` and lead to the false conclusion
that no device-read instrument exists — which then sends you back to Central reads, which is the exact
failure this whole section is written to prevent. **A `null` means "wrong call", never "no such
capability". Check the enum before concluding you are blind.**

### show configuration failure is a HISTORY, newest first

It accumulates (24+ entries observed). **Read the HEAD, not the tail.** Tailing it shows the OLDEST
failures and sends you chasing errors that were resolved hours ago.

Correlate every entry's ConfigId against the live one in `show switches`:

```
show switches  ->  Configuration State: CONFIG FAILURE(118)   Config ID: 119
```

Config ID **119** with the newest failure at **118** means the latest push SUCCEEDED — the state string
is a sticky label naming the last *failed* id, not current health. Central flattens this whole history
into a single `topPriorityIssue` string, mixing stale and current, which is exactly how hours get spent
on an error that no longer exists.

### The compiled ACL is named sys_policy_<ROLE>, not <policy-name>

Central compiles an intent-based policy into a device ACL named after the **role**. So:

```
Message: Unknown access-list 'MyPolicyName'
```

may be **spurious** — Central emits a raw `access-list session <policy-name>` binding alongside the
compiled one, and the device rejects the former while correctly applying the latter. Do not act on this
error until you have checked what the role actually holds:

```
show rights <ROLE>                              # position list + ACE table of sys_policy_<ROLE>
show running-config | include "ip access-list session"
show running-config | include <policy-name>     # empty => never persisted; push-time only
```

If `sys_policy_<ROLE>` contains your intended rules, **the policy is live** regardless of that failure line.

### A policy with no substantive rules emits NO ACL

A policy whose only rule is `role -> any: permit` compiles to zero ACEs. The ACL is never created while
the role still references it by name — a self-inflicted `Unknown access-list`. **A placeholder policy
must contain at least one real match**; a deny to an RFC 5737 documentation prefix such as
`192.0.2.0/24` is a safe non-empty no-op.

### Neutralising a policy without deleting it

Never delete a policy a role references — the role keeps a dangling reference the merge-only API cannot
clear, and **every subsequent push to that device fails**. To make a policy harmless in place, repoint
its deny destinations at RFC 5737 documentation prefixes (`192.0.2.0/24`, `198.51.100.0/24`,
`203.0.113.0/24`). The ACL stays non-empty and renders; it blocks nothing.

---

## 5c. Before diagnosing a tunnel WLAN, confirm a client is actually associated

Every tunnel-mode datapath counter reads "empty" when nothing is associated, and empty looks identical to
broken. Establish there is a client BEFORE interpreting any of it:

```
show ap bss-table          (on the AP)   # is the ESSID being broadcast, on which radios
show ap association        (on the AP)   # cur-cl / client rows -- zero means an empty network
show user-table            (on the GW)   # "User Entries: 0/0" == nothing to debug
show datapath tunnel       (on the GW)   # AP GRE entry count -- tunnel health, independent of clients
```

If `show ap association` is empty on **every** SSID, the network is idle, not faulty. An SSID that is
broadcasting on both radios with zero associations and a healthy GRE tunnel is a network waiting for a
client — no amount of further reading will produce a fault, because there is not yet any traffic to fail.

**Only a real client association proves a tunnel-mode WLAN works.** Config being correct at every layer
proves only that it should.

---

## 5d. Additional client VLANs on a shared AP↔gateway tunnel — what is established, and what is NOT

One GRE tunnel carries MANY client VLANs; they are 802.1Q-tagged inside it. If you conclude "gre0 only
carries one VLAN", treat that as a symptom, not a platform limit — multi-VLAN tunnel mode is standard
campus design.

**Doc-established requirement (Tunnel Forwarding Mode page):**
> "Each tunneled client is either statically or dynamically assigned to a VLAN, **which is present on all
> the gateways within the primary cluster**." · "the user VLANs are centralized and reside within each
> cluster… Each gateway within a cluster shares management VLAN, user VLANs, and associated IP networks."

**Also doc-established: a SINGLE-gateway cluster is a supported, documented topology** —
> "This example uses a single gateway to simplify the datapath of each tunneled client."

So `ISOLATED (Leader)` / one member is **not** inherently disqualifying, and a VLAN that is defined,
enabled, addressed and on the tunnel ports of that one gateway satisfies the stated requirement.

### ⚠ Two dead ends — do NOT read these as evidence (corrected 2026-08-28)
- **The AP's `show vlan` "Vlan Mapping Table" is the NAMED-VLAN table** (`VLAN Name → VLAN ID`). If the
  deployment does not use Named VLANs it is empty **by design**, and its emptiness says nothing about
  what the tunnel carries. An earlier revision of this skill claimed an empty table meant "the AP learned
  no cluster VLANs" — **that was wrong** and is withdrawn.
- **The cluster VLAN probe is peer detection, not AP advertisement.** It is a Layer-2 unicast
  (etype `0x88b5`) used to determine whether a *peer gateway* is L2- or L3-connected. On a single-node
  cluster an empty probe table is expected, not a fault.
- Beware the citation trap that produced both: the "VLANs present in the clusters are **learned by the
  APs** and are tagged in the GRE tunnels" language is on the **Mixed Forwarding Mode** page. Do not
  carry it onto tunnel mode without checking the tunnel-mode page itself.

### Overlay SSID on the AP's UNDERLAY VLAN — what is established, and what is NOT

**CORRECTED 2026-08-28 (second revision).** An earlier revision of this skill stated flatly that a
tunnel-mode SSID cannot use the AP's underlay VLAN. **That was overgeneralised from a single SSID and is
wrong.** The corrected, evidence-bounded position:

| SSID type | VLAN source | Underlay VLAN | Result |
|---|---|---|---|
| Open + cloud-NAC portal | VAP-derived | underlay (VLAN 1) | **FAILS** — `Underlay VLAN on overlay SSID` |
| Open + cloud-NAC portal | VAP-derived | dedicated client VLAN | works |
| **802.1X** | **role/RADIUS-assigned** | **underlay (VLAN 1)** | **WORKS** — `dtunnel`, tunnel ID + VLAN 1 confirmed |

So the failure is **specific to the VAP-derived-VLAN path**, not to overlay-on-underlay in general.

**The instrument that names it — run it ON THE AP:**
```
show ap debug vlan          # "VLAN Assignment Failure Table": time / mac / bssid / REASON / description
```
In the failing case it logged 17 entries, all the same reason, all while the SSID sat on the underlay
VLAN, and **zero** after moving to a dedicated client VLAN. The reason string names `derive_vlan_from_vp`.

**Hypothesis, NOT established:** that the VAP-derived and RADIUS/role-derived VLAN assignment paths are
validated differently against the underlay VLAN. The `derive_vlan_from_vp` reason string points that way.
Do not build a design on it without testing.

**Practical guidance that survives both revisions:** give tunnelled SSIDs their own client VLAN. It costs
nothing, it is the documented design, and it side-steps this entire class of fault — but do NOT tell a
customer their 802.1X SSID is broken because it sits on the underlay VLAN, because that is demonstrably
not true.

**These were NOT the fix** in the failing case: the gateway `vlan-interface`, the policy scope, the
VLAN's IP address, the role ACL, and a full WLAN rebuild.

**`gre0` showing a single VLAN is not the limit** — it still reads `VLANs 1` while a dedicated client
VLAN forwards correctly. Treat it as a symptom, never a constraint.

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
- The **bucket map published by the cluster leader** assigns each client's UDG.
  **CORRECTED 2026-08-28:** an all-zero bucket map is NOT a fault on a single-node cluster. The values are
  UAC *indices*, so with one gateway every bucket is `00` = "UAC 0" = the only gateway. Verified with two
  tunnelled SSIDs carrying authenticated clients while the map read all zeros end to end. Only treat zeros
  as a fault when the cluster has MORE THAN ONE member and you expect a spread.
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

- **A tunnel-mode WLAN MUST be a Library (SHARED) profile. This is documented, not incidental.**
  New Central config guide, *AOS-10 APs and Mobility Gateways Configuration*: "You must create tunnel-mode
  WLAN profiles in the **Library** and assign them to the **device groups** containing the APs that service
  the ESSID… Future updates will add support to assign WLAN profiles to any scope in the hierarchy,
  including Global, Site Collections, Sites, Devices, and Device Groups."
  In the Create WLAN dialog this shows up as: tick **"Create as a local profile"** and the **Tunnel** and
  **Mixed** radio buttons DISAPPEAR — Bridge becomes the only forwarding mode. Untick it and they return.
  **Consequence:** you cannot have a tunnel-mode WLAN *and* site-local AAA references. A SHARED WLAN
  **cannot reference a site-LOCAL server group** — `Cannot find in library '<name>' of type
  'aruba-auth-server-group' referred in '<ssid>' of type 'aruba-wlan'`. So any "lab override that dies at
  the site boundary" pattern is unavailable for tunnel SSIDs: promote the AAA objects to the Library, and
  label them so they are removed when the gateway moves.
  **Also assign it where the doc says.** Assignment belongs on the DEVICE GROUP containing the APs. Site
  scope may appear to work — it did in a real build — but the doc lists site-level assignment as a FUTURE
  capability, so it is not guaranteed across upgrades. Call the deviation out rather than relying on it.
- **Tunnel is the prescribed mode once a gateway is in the design.** Same doc: "You **must** select
  **Tunnel** for AP and Mobility Gateway deployments. The **Bridge** option is for AP-only deployments.
  The **Mixed** option is for AP and Mobility Gateway, but allows some VLAN to be trunked to the switching
  fabric based on user session VLAN assignment." Bridge is the controller-less/AP-only architecture.
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

## 9c. Guest captive portal — what AOS 10 does and does not offer

Do NOT reason about this from the UI drop-downs; it is documented and the docs are unambiguous.

- **The AP is the authenticator; the gateway is an authentication PROXY.** AOS 10.x tunnel-mode doc: "APs
  function as authenticators and send authentication and accounting requests to the Gateway cluster…
  The AP acts as an authenticator… The Gateway acts as an authentication proxy." Captive-portal
  interception and redirect happen at the AP even for a tunnelled SSID.
- **There is NO on-prem splash-page host in AOS 10 campus.** The AP guest doc lists exactly two supported
  splash page profiles: **External Captive portal** and **Cloud Guest**. Neither is AP-hosted. The
  `securelogin.hpe.com` cert on the AP group terminates the intercepted TLS session — it does not serve
  portal content. The gateway does not host a portal either (see next point).
- **The gateway captive-portal profile you will find in the CLI is the BRANCH GATEWAY path.** `show aaa
  authentication captive-portal` returns a `default` profile on a campus Mobility Gateway and the web
  server has a Captive Portal Certificate — this is misleading. The Central doc for configuring it is
  scoped to "a group that contains at least one **Branch Gateway**" and its video is
  `l3-cptv-prtl-bgw-adv-mode.mp4` (bgw = Branch GateWay). It is SD-Branch, not campus tunnel-mode WLAN.
- **New Central has three WLAN Security Levels: Enterprise, Personal, Open.** There is no "Visitors"
  level. Cloud Guest attaches to "Visitors" in CLASSIC Central only. So on New-Central-managed devices the
  guest portal is **Central NAC** or **External Captive Portal** — nothing else.
- **A Central-NAC SSID cannot be localised at any scope.** Both API and UI reject it identically:
  `For LOCAL SSID, Can not use Central NAC server as the server group.` Plan for it: a guest SSID on
  Central NAC can never take a site-level override (VLAN or otherwise). If the deployment needs a per-site
  guest VLAN, that VLAN must exist on the wired side, or the portal must be External.

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

**Third pass, same day — grounded in the vendor docs after the Human rejected trial-and-error findings.**
§9b's shared-vs-local rule and §9c (guest captive portal) were originally derived by clicking through the
UI. That produced the right answers twice and a WRONG answer once (an invented "AP-hosted portal" option,
read out of an ambiguous doc sentence). All three are now sourced:

- new-central `get-started/cfg-guides-ap-gw.htm` — tunnel WLANs must be Library profiles assigned to the
  AP device group; Tunnel is mandatory for AP+Mobility Gateway deployments; Security Levels are
  Enterprise / Personal / Open only.
- aos10x `cfg/cfg-wlan-overlay.htm` — APs are authenticators, the gateway is an authentication proxy.
- aos10x `cfg/aps/conf_guest_ssids.htm` — the only two splash page profiles are External and Cloud Guest.
- aos10x `cfg/security/authentication/l3-cptv-prtl-conf.htm` — the gateway captive-portal profile is the
  Branch Gateway path.

**Do not report a capability question from UI presence or absence.** A drop-down tells you what this
tenant exposes today; the doc tells you what the product does and why. Read §0 and go to the doc first.
