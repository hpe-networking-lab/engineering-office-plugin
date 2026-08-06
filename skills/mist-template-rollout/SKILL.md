---
name: mist-template-rollout
description: Roll out or change a Juniper Mist template safely — golden object, lint, inert deploy, render
  gate, verify against the consuming object. Use whenever a Mist WLAN / RF / switch / network / site
  template is created or edited in an org, or when a Mist config write "succeeded" but didn't take effect
  or crashed the UI. Trigger words: Mist template, WLAN template, RF template, switch template, site
  variables, render gate, deploy config to Mist, template page crash, golden object, coa_servers,
  dynamic_vlan.
---

# mist-template-rollout

> The ordered, safe path for creating or changing any Mist template. It prevents the two failure classes:
> (a) a write that "succeeds" but never takes effect, and (b) a schema-valid payload that **crashes the
> Mist UI** so the customer can't see it. **Self-contained + configurable:** it uses *your* Mist connector
> and *your* OpenAPI spec / linter (from `scripts_dir` if you have one). If your `standards_source` defines
> a binding Mist template playbook, **read and follow it first — authoritative** (it may grow); the steps
> below are the portable floor. Governing: [[eo-guardrails]] — render gate, verify the consuming object,
> org by ID, secrets, Human-Authority approval for customer-org writes. Baseline first with
> [[config-backup]].

## Golden rules (non-negotiable)

- **Never write a customer org without Human Authority approval.** Read-only until approved. Reference the
  org **by ID**, never by name.
- **Inert first.** New WLANs `enabled:false`; templates left unassigned. Activate only on approval,
  **site-by-site, with a tested revert path**.
- **Record every created object (name + id)** for a clean revert.
- **Secrets out-of-band only** (RADIUS/ISE secret, PSKs, claim codes) — from your `credentials_file`;
  presence, never value.
- **Check org alarms before and after** any write; expect **0 → 0**. Copy/paste for the operator = a
  single clean fenced code block.

## Procedure (in order; never skip lint or the render gate)

### 1. Build from a golden object — never sparse hand-authored JSON
UI-render crashes come from minimal payloads that omit sub-objects the UI assumes exist.
1. Create one object of each kind **in the Mist UI** (or clone a known-good template), then `GET` it.
2. Use that as the canonical payload; swap concrete values for `{{variables}}`.
3. The UI-made object carries every sub-structure the UI renders (`dynamic_vlan.vlans`, ratesets, portal
   bodies, `port_usages`, `networks`) — your API object inherits the complete shape.

### 2. Pre-deploy lint — catch what schemas can't
Lint every payload against your Mist OpenAPI spec (path from your config/`scripts_dir` linter if you have
one) and fix all ERRORs before writing. Known traps:

| If … | Require … | Else the failure is |
|---|---|---|
| `wlan.dynamic_vlan.enabled` | non-empty `vlans` **or** `default_vlan_ids` | UI `Object.keys(undefined)` → template page crash |
| `wlan.dynamic_psk.enabled` | `wlan.auth_servers` | dynamic PSK is RADIUS-sourced → invalid |
| `wlan.auth.type == eap` | `wlan.auth_servers` | 802.1X with no RADIUS server |
| `wlan.portal.enabled` | a portal body | empty portal editor faults |
| any field | not `deprecated` in OpenAPI | UI may read only the successor field |

Field gotchas confirmed the hard way — check explicitly:
- `coa_servers[]` uses **`ip`**, not `host` (auth/acct servers use `host`). Wrong key → CoA silently dead.
- Site **variables** live on the **Site Setting** object `/sites/{id}/setting` `vars`, **not** the Site
  object — the Site object accepts them silently and the UI shows 0 variables.
- `dynamic_vlan.default_vlan_id` is **deprecated** → use `default_vlan_ids` (array).
- Maps (`vars`, `port_usages`, `networks`) validate on **values**, not their arbitrary keys.

### 3. Deploy inert
WLANs `enabled:false`; templates unbound. Capture org alarms first, POST/PUT, capture again → expect
**0 → 0**. Write the revert manifest (object names + ids) to your engagement deploy record.

### 4. Render gate — a template isn't "done" until its page renders
The definitive, cheap catch. Verify in the **actual consumer** (the UI), not just read-back:
1. List every affected template's page URL.
2. Open each in the Mist UI (a browser automation tool), click the row, read console **errors only**.
3. Clean pass = **no** `TypeError` / `Cannot convert undefined or null to object` / "unexpected error".
   On a hit, the JS stack names the renderer + field — fix **that** field, don't guess. Hard-reload between
   fixes so cached JS doesn't mask a change.
- Reproduce render bugs in the browser and read the error; schema validation can't see a renderer assuming
  a sub-object exists.

### 5. Verify against the consuming object
Read back from the object the system uses (Site Setting for vars; the WLAN the UI renders), not the field
you wrote. A write succeeding proves nothing. Hardware-only items (variable substitution on a live device,
LACP/STP/native VLAN) are **deferred to bring-up** — flag them, don't mark done.

### 6. Activate (only on Human-Authority approval)
Site-by-site, in a maintenance window, revert manifest ready. Enable WLANs / bind templates one site at a
time; re-run the render gate and alarm check after each.

## Pre-flight checklist
- [ ] Built from a UI-golden/cloned object. [ ] Lint passes — 0 ERRORs. [ ] `coa_servers.ip`, Site-Setting
`vars`, `default_vlan_ids` verified. [ ] Deployed inert; alarms 0→0; revert manifest written. [ ] Render
gate clean on every affected page. [ ] Read-back verified against the consuming object; hardware checks
deferred. [ ] Secrets out-of-band. [ ] Activation only on HA approval, site-by-site, revert ready.
