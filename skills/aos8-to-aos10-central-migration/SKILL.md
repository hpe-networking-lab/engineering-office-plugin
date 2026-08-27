---
name: aos8-to-aos10-central-migration
description: Migrate controller-managed ArubaOS 8 campus APs to AOS 10 under HPE Aruba New Central —
  onboarding, entitlement, group and site assignment, the controller-side ap convert flow, and rebuilding
  WLAN/VLAN/RADIUS config in the Central config model. Use for AOS8 to AOS10 migrations, AP conversion,
  hybrid Classic+New Central tenants, converted APs that are Out of Sync or broadcast nothing, and
  standalone-vs-hybrid deployment-mode decisions. Trigger words: AOS 8, AOS 10, ap convert, pre-validate,
  campus AP migration, New Central, Classic Central, hybrid cluster, device-group, device-collection,
  API_ACCESS_RESTRICTED_IN_HYBRID_CLUSTER, No group(Central), OUT_OF_SYNC, config push failures,
  AirWave parity, GreenLake claim, AP subscription.
---

# AOS 8 → AOS 10 campus AP migration (New Central)

A migration runbook distilled from a full POC plus a lab dress rehearsal. Nearly every gate here was
paid for with hours lost or a wrong answer given to a customer.

**Scope:** controller-managed Campus APs moving to AOS 10 / New Central. Mobility Gateway system-IP,
cluster and tunnel-anchoring work is a *different* problem — use `aos10-gateway-tunnel-build`.

---

## 0. Two rules that prevent most of the pain

1. **Read the vendor procedure first, then confirm it in the lab.** The lab confirms the doc; it does not
   invent a procedure. Reverse-engineering the Central API by trial and error is how this migration went
   wrong repeatedly.
2. **Config is RECREATED in the Central config model, never cloned verbatim from the controller.** A
   verbatim clone of an AOS 8 controller config produces "Custom mode" WLANs full of `no <field>` lines
   that AOS 10 rejects, plus country-code and AP-System profile churn. Recreate to the reference design;
   for a POC that means minimal, not full replication.

**Authoritative docs**
- Validated Solution Guide — ESP Campus Migrate:
  `arubanetworks.com/techdocs/VSG/docs/035-campus-migrate/esp-campus-migrate-060-aos8to10upgrade-steps/`
- Migrating APs to AOS 10 (Central techdocs): `.../content/aos10x/cfg/aps/ap-migration.htm`
- Migrating to AOS 10 (index): `arubanetworking.hpe.com/techdocs/aos/aos10/migrate/`
- New Central hierarchy: `developer.arubanetworks.com/new-central/docs/new-central-hierarchy`
- Official workflow reference: `github.com/aruba/central-python-workflows` → `device-onboarding/onboarding.py`

**HARD SIGNAL:** if you find yourself doing token gymnastics to satisfy a prerequisite — CORS dodges,
`window.name` bridges, swagger hacks — stop. That is the sound of being off the documented procedure.
(The one exception below is documented: the Classic `devices/move` call, which Aruba's own onboarding
workflow performs.)

---

## 1. Establish cluster type BEFORE planning anything

Everything downstream forks on this. If the tenant shows a **"Classic Central" toggle**, it is a
**hybrid** cluster (Classic + New Central coexisting). New Central today *is* the hybrid model — there is
no Classic-free New Central yet.

| Operation | Pure New Central | Hybrid |
|---|---|---|
| Device → group membership | native group-add API | **Classic `configuration/v1/devices/move` only** |
| Group CREATE | native | **Classic `configuration/v3/groups`** (see §3) |
| Site create | API works | API works |
| Site device-assign | API | **Classic UI drag-drop** |
| Config-model writes (WLAN/VLAN/AAA/role) | works | **works** — not blocked |

The New Central config-write APIs return HTTP 400 `API_ACCESS_RESTRICTED_IN_HYBRID_CLUSTER` for
**membership** operations only. Do not conclude the whole New Central config API is blocked because
device-move was.

---

## 2. The prerequisite chain — verify each link LIVE

A handoff saying "the AP is onboarded, just set persona / move the group" is a claim, not a fact. Verify
the whole chain from the top; the real blocker is usually further upstream than the handoff claims.

**Gate 1 — GreenLake claim + entitlement (mode-independent, and the customer's recurring friction).**
- The device must be claimed into *this* workspace's GreenLake inventory with a service assignment.
- UI: Asset Explorer → Actions → Assign to service → HPE Aruba Networking Central + region → Finish.
  Lands in New Central inventory in ~2 minutes, no Classic, no API.
- API: `PATCH /devices/v1beta1/devices` with `{"application":{"id":"<service-manager UUID>"},"region":"<region>"}`,
  then a **second** PATCH `{"subscription":[{"id":"<sub-resource-id>"}]}`. Two separate PATCHes — not one.
  The bulk-add tool 500s and will not enrich an already-claimed device.
- **Verify the subscription is VALID, not merely available.** Check `subscriptionStatus` / `endTime`, NOT
  `availableQuantity`. An expired eval still reports availableQuantity > 0, and then the assignment fails
  async with no reason, the UI says "no subscription available to select", and `ap convert` pre-validate
  fails `No license(Central)`.
- A **used / hand-me-down AP** is locked to the prior owner's GreenLake account and must be released
  there first. It also still carries the prior owner's config and credentials. The serial is not on the
  wire (LLDP gives the MAC) — you need the label or a factory reset.

**Gate 2 — persona.** New Central → Device Inventory → select AP → Assign → Campus Access Point.
This panel sets device FUNCTION **only** — it offers no group and no site control. That is a UI reality,
not an API artifact.

**Gate 3 — group membership.** `ap convert pre-validate` HARD-REQUIRES it (see §4). Persona plus
subscription is not enough; pre-validate returns `No group(Central)` until the AP is in a Central group.
You cannot dodge this by staging config at Global scope — Global helps config *apply* after the AP joins,
but the controller blocks the *conversion* on group membership.

**Gate 4 — site.** Provisioning State = Yes needs site + license + persona. An AP with no site connects
to Central (`Login_done`) and sits factory-default broadcasting nothing.

---

## 3. Create the group the RIGHT way, or config will never deploy

The most expensive silent failure in this migration: an AP that is online in Central, in a group, and
**Out of Sync with no SSIDs on air**, because the New Central config **device-collection** deviceCount
stayed 0 and group config therefore never deployed.

A Classic `devices/move` succeeds and genuinely puts the AP in the Classic group — but does **not**
populate the New Central device-collection **if the group was created the wrong way** (e.g. via the UI
without the right attributes).

**Create the group via the Classic API:**
```
POST /configuration/v3/groups
{
  "group_attributes": {
    "group_properties": {
      "Architecture": "AOS10",
      "ApNetworkRole": "Standard",
      "NewCentral": true,
      "AllowedDevTypes": ["AccessPoints"]
    }
  },
  "template_info": { "Wired": false }
}
```
Then, in order:
1. Confirm the group appears in `GET /network-config/v1/device-groups`.
2. `POST /configuration/v1/devices/move` `{"group":"<AOS10 group>","serials":["<serial>"]}` → 200 Success.
3. **Confirm deviceCount > 0 BEFORE converting.** This is the check that catches the silent failure.

If you build the group in the UI instead, verify deviceCount the same way — a UI-made group that stays at
0 after a successful move is the known-bad case; rebuild it via the API.

**Classic token:** the Classic API-Gateway is a *separate host and separate OAuth token* from New Central.
A New Central / GreenLake token returns 401 there. Mint the Classic token from Classic Central → API
Gateway → My Apps & Tokens → Add Apps & Tokens → Generate (issues from your session, no password); TTL is
about 2 hours, and a refresh-token grant can self-mint thereafter. Store it in your secrets path, never in
chat. Delete the app afterwards to revoke.

---

## 4. The conversion itself (controller-side)

Run from the controller/gateway. Prereqs per the docs: gateway on 8.7.1.9 / 8.10.0.5 or later, APs on
8.7.1.0+, and each AP must reach the cloud.

```
ap convert add ap-name <ap-name|mac>          # or: ap convert add ap-group <group>
ap convert pre-validate specific-aps          # answer y — NON-destructive readiness check
show ap convert-status                        # want: Pre Validate Success + Central Group populated
ap convert cancel                             # REQUIRED, else 'active' says "already executed"
ap convert active specific-aps activate       # destructive: downloads AOS10 and reloads; answer the
                                              # country-code prompt y
show ap convert-status                        # Downloading Image -> Update Done
```

- **Use a PTY.** A one-shot ssh command cannot answer the `[y/n]` prompts. Drive it over an interactive
  session (paramiko `invoke_shell`, or equivalent).
- `ap convert` is exec-only — it is not in the AOS 8 connector tool set. SSH is the path.
- After conversion the AP checks into Central under the assigned group. Confirm on the AP itself:
  `show ap debug cloud-server` → "Aruba Central status: Login_done".
- **Revert (proven):** on the AP console, `convert-aos-ap cap <controller-ip>` re-images back to an AOS 8
  campus AP in roughly 5–10 minutes and gives a clean default state. `ap wipe out flash` is FIPS-only.

**Mental-model fix that costs hours if you miss it:** a not-yet-converted AP does **not** appear in
Central's operational Devices / Groups / Sites lists — only in the pre-provisioning **inventory**.
"0 devices in Classic" is expected, not a blocker.

---

## 5. After conversion — the three things that leave an AP silent

**a) Assign the AP to a SITE.** In hybrid this is a Classic Central action: toggle Classic → Global →
Maintain ▸ Organization ▸ Network Structure ▸ Sites tile → select "Unassigned" → drag the device onto the
target site. The New Central Device Assignment panel cannot do it, and the site-assign API returns 400
`API_ACCESS_RESTRICTED`. A re-provisioned or re-converted AP lands Unassigned again.

**b) ENABLE each WLAN.** New Central creates WLAN profiles **Disabled** by default. Symptom: AP online,
Configuration Status = Out of Sync, no SSIDs, empty `show ap bss-table`. A valid country code is necessary
but not sufficient. Fix: Config (device-group scope) → Wireless → WLAN → row kebab → Enable → confirm.
Per SSID.

**c) Set the fields that stop Central emitting `no <field>`.** Central emits `no <field>` for WLAN fields
left UNSET, and AOS 10 rejects the whole block → CONFIG_PUSH_FAILURES / OUT_OF_SYNC, sometimes while the
SSID is still on air. **Include these in the CREATE payload from the start:**
```
dtim-period: 1
broadcast-filter-ipv4: BCAST_FILTER_ARP
dmo: { "channel-utilization-threshold": 70 }     # MUST be non-default; a default value is
                                                 # optimized away and re-emits `no`
```
`dmo` **is** an exposed container — an early conclusion that it was unsettable and needed TAC was wrong.
A resync does not fix this; it re-pushes the same `no` lines. In the UI the DMO threshold field is
read-only until the "Dynamic Multicast Optimization (DMO)" checkbox is ticked.

Do **not** attribute these push failures to AP firmware. That theory was tested and disproved — the same
failures persisted after upgrading the AP.

---

## 6. The scope model — where config actually lives

Hierarchy: **Library > Global > Site Collection > Site > Device**, and a device inherits from every level
above. **Device Groups are a separate optional construct that cuts across the hierarchy and apply
DEVICE-level config, which has the HIGHEST precedence.**

That single fact explains a symptom that looks like broken inheritance: WLANs defined at a Site scope did
not reach an AP, and the AP stopped broadcasting — not because site scope is broken, but because the
device group the AP sat in was overriding it. To run the site/collection-scoped model, the APs must not
sit in a WLAN-bearing device group.

Practical consequences:
- Read the hierarchy doc **before** relocating config across scopes, and prove the on-air result before
  doing it on a live or customer AP. Success from the API is not "applied".
- A scoped GET returns **SHARED / effective** objects (inherited, merely visible), not objects defined and
  assigned at that scope. Editing at that scope then fails `... name='X' doesn't exist`. Confirm an
  object's real home via `aruba-annotation:scope_device_function` on a `detailed=True` read.
- The instance the connector can PATCH is the **device-collection-scoped** one. You CAN assign a shared
  WLAN at a site-collection scope (it inherits down and broadcasts), but you CANNOT patch its fields there
  via the API — use the UI for that edit.
- Verify WLAN placement in the New Central UI (Device Group scope → Wireless → WLAN Manage); scoped API
  reads have failed to reflect freshly created profiles.

**Rehoming SSIDs to the shared inherited model** (defined once at the collection, inherited to all member
sites): assign `wlan-ssids` + its `layer2-vlan` + (for 802.1X) `auth-servers` and `server-groups` at the
collection scope → fix the `no <field>` rejections that then appear on the *other* site's AP via the UI →
remove the old per-site duplicates. Gotchas: removing a `wlan-ssids` assignment auto-removes its dependent
`roles`/`role-gpids` (removing them separately 400s `not scope-mapped`); the row action is **Delete** for
a scope-local object but **Unassign** for a shared one; the connector's remove action type is `remove`.

---

## 7. RADIUS / 802.1X

- **The auth-server shared secret is not in the config-model API.** The `auth-server` object's full field
  set contains no `shared-secret` / `key` / `secret`. Build everything else by API (address, ports,
  `type: RADIUS`, `radius-server-mode: AUTH_AND_COA`, CoA, server-group binding, WLAN 802.1X) and treat the
  secret as the one UI / out-of-band step.
- **A secret mismatch is silent.** ClearPass masks `radius_secret` in every GET (always returns ""), so you
  cannot verify it by API, and on a mismatch it **discards packets per RFC**: zero hit count, no Access
  Tracker entry, nothing. That is indistinguishable from "the AP isn't sending" — do not draw that
  conclusion. Set the same secret on **both** ends in the UI, then prove with a real client.
- `server-group` requires `servers: [{"server-name":"<auth-server>","position":1}]` — `position` is
  mandatory or the WLAN config-assignment fails. The referenced auth-server must exist first.
- In the WLAN editor the "Server Group" dropdown offers only "Primary And Backup Only" / "Central NAC" —
  an API-created server-group does not appear there. Bind the RADIUS server via **Primary Server**.
- WPA2-Enterprise / legacy key management is greyed out until you **disable the 6 GHz band and Wi-Fi 7**.
- **The WLAN editor blocks Save SILENTLY on an invalid field deep in Advanced.** The usual culprit is an
  empty *Max Clients (Per Radio, Per AP)* — a red inline error only visible after scrolling. Scroll the
  entire form before assuming something exotic.
- "Client authenticates but has no IP" is a DHCP/infra item on that VLAN, not an auth failure.

---

## 8. What the connector can and cannot do (hybrid tenant)

- **Config-model writes work:** WLAN profiles, auth-servers, server-groups, VLANs, roles, config-assignments.
- **Membership writes are blocked:** device-groups-add-devices, device-collection-add-devices, site
  device-assign.
- **Some management-plane writes return `null` — a silent no-op, not an error.** Observed on GreenLake
  device-add, floor/building create, and report create. Do not treat a null as success; re-read to verify.
  This is **not** universal: `central_manage_site` create/update/delete returns real success. Try the API
  first, fall back to the UI only when a specific call actually returns null.
- `central_resync_device_config` needs `confirmed: true` passed inside params via the invoke-tool form.
- Schema introspection trick: a 400 whose message ends `valid body fields: ...` enumerates that node's
  direct children. POST a bogus child to list fields — but only ONE probe write per execute block, since
  the sandbox aborts the block on the first write error.
- Browser automation cannot perform HTML5 drag-and-drop (Groups table, Manage Sites) — it text-selects.
  Use non-drag controls or hand the drag to a human.

---

## 9. Verification — the green signature

Do not declare a migration done on any single signal, and never from an earlier check.

```
central_get_device_config_issues      -> all four arrays empty
central_get_devices_config_health     -> configStatus SYNCHRONIZED, activeIssues []
central_get_wlans_monitoring          -> status ENABLED (expect ~1 min lag after a change)
on the AP: show ap bss-table          -> BSS present per SSID/band
on the AP: show network               -> SSIDs Enabled
on the AP: show ap debug cloud-server -> Aruba Central status: Login_done
```
The AP's own CLI is authoritative; Central monitoring lags. After a delete, `central_get_wlans_monitoring`
can show the old count for a minute — re-poll before concluding the write was a no-op. Per-AP `wlanCount`
lags too; trust the monitoring total plus SYNCHRONIZED.

---

## 10. Deployment mode: standalone vs hybrid

Separate the axes: **standalone vs hybrid = management plane**; **Foundation vs Advanced = feature
license**. Do not choose on onboarding friction alone.

If the customer's adoption gate is a set of monitoring/ops views (the AirWave-parity case — RAPIDS,
Clarity / client connectivity, Reports, Floorplans), weigh feature **maturity**: those views are mature in
Classic Central while several were still Early-Access or filling parity in New Central. So onboarding
friction favours standalone (backstage, the SE absorbs it) while the customer-facing parity demo often
favours hybrid. Verify per-view GA **in the customer's own tenant** before promising either.

Related trap: **do not declare a Central feature "gated / Select Availability" from a config-model API
error alone.** An AP firmware upgrade was called gated on that basis and the conclusion was wrong — the
Firmware Management UI wizard was fully functional (Global → Firmware Management → Create Firmware Policy,
Device Function = Campus Access Point, full version list). The config-model API is a different and newer
surface than the shipping UI. Check the UI before putting anything on an enablement request.

And when grading capability parity for a customer, grade against the artifacts they actually sent — the
screenshots, exports and configs — not a prior chat's summary of them. Summaries under-scope and
over-grade, and license tier plus migration effort are exactly what decides the deal.

---

## 11. Order of operations (the short version)

1. Determine cluster type; read the VSG and migration docs.
2. Claim device in GreenLake + attach a **valid** subscription. Verify entitlement, not availability.
3. Set persona = Campus Access Point.
4. Create the AOS 10 AP group via Classic `configuration/v3/groups` with the right attributes.
5. `devices/move` the AP into it; **confirm New Central deviceCount > 0**.
6. Recreate WLAN / VLAN / AAA config in the Central config model at the device-group scope, WITH the
   anti-`no`-line fields, and bind `wlan-ssids` with an explicit config-assignment.
7. Controller: `ap convert add` → `pre-validate` → `cancel` → `active`.
8. Assign the AP to a site (Classic drag-drop).
9. Enable each WLAN.
10. Verify the green signature on the AP, not in Central alone.

---

## Provenance

Distilled from a live AOS 8 → AOS 10 campus-AP POC and lab rehearsal (2026-08). Several gates here
supersede earlier conclusions from the same effort that were later disproved — the firmware-floor theory,
the "dmo needs TAC" note, the "site scope is broken" reading, and the "firmware upgrade is gated" call.
Where this file and the practice's canonical lessons record disagree, the canonical record wins — fix
this file. Gateway/tunnel work is out of scope: see `aos10-gateway-tunnel-build`.
