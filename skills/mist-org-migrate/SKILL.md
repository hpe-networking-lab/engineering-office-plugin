---
name: mist-org-migrate
description: Consolidate one Juniper Mist org into another safely — clone the config, release devices from
  the source and claim them into the target, then run the interop gate — referencing orgs and sites by ID
  only. Use whenever devices/config are moved or merged between Mist orgs, an org is consolidated or
  decommissioned, or a tenant migration is planned. Trigger words: Mist org migration, consolidate orgs,
  merge orgs, move devices between orgs, release and claim, org decommission, tenant migration, org by ID.
---

# mist-org-migrate

> Move/merge one Mist org into another without losing config or bricking devices: **clone config →
> release/claim devices → interop-gate verify**, always addressing orgs/sites **by ID, never by name**.
> Change-making, cross-org — **fully gated**. **Self-contained + configurable:** uses your Mist connector
> and OpenAPI spec; if your `standards_source` has an org-migration runbook, follow it as authoritative.
> Build payloads/gates on [[mist-template-rollout]]; baseline first with [[config-backup]]. Governing:
> [[eo-guardrails]] — reflex 7 (ID not name), reflex 8 (customer-org writes → Human Authority), reflex 4
> (claim codes/secrets out-of-band), reflex 1 (verify the consuming object). Ground exact endpoints/fields
> against your Mist OpenAPI — do not hand-author from memory.

## When this fires

"Consolidate org A into org B", "move these APs/switches to the other org", "merge the two Mist tenants",
"decommission the old org and bring its devices over".

## Golden rules (non-negotiable)

- **Orgs and sites by ID only.** Every read/write targets a stable **org_id / site_id**, never a display
  name. Confirm both source and target IDs before any write.
- **Never write a customer org without Human-Authority approval.** Both source and target read-only until
  approved. This writes to *two* orgs — approval covers both, with a change window + rollback.
- **Release is disruptive to the device.** Releasing drops it from the source org's management; plan the
  window, have the target ready to claim so downtime is bounded. One site/batch at a time.
- **Claim/activation codes are secrets** — out-of-band, from your `credentials_file`; presence, never
  value; never in chat or git.
- **Check alarms on both orgs before and after**; expect no new alarms attributable to the move.

## Procedure

1. **Baseline both orgs** ([[config-backup]] against each org_id) — templates, WLANs, site settings, device
   inventory, access-assurance. This is the diffable "before" and rollback reference. Record source/target
   **org_id** and the device list (name + **id/MAC**) to move.

2. **Clone config into the target first (inert).** Recreate needed org/site/template objects in the target
   **from golden objects** ([[mist-template-rollout]]: golden → lint → inert → render gate → verify).
   Variable-driven payloads; validate against the OpenAPI. Do this **before** touching devices so the
   target is ready to enforce policy on claim.

3. **Release devices from the source** (by device id, in planned batches), confirming each leaves the
   source inventory cleanly. Keep the revert manifest (device ids + original site) current.

4. **Claim devices into the target** (claim code out-of-band) and assign to the correct target **site_id**.
   Expect them to adopt the cloned config.

5. **Interop gate — verify to the consuming object.** Confirm each device is managed by the target org, on
   the intended site, pulling the cloned template, and that dependent interop (NAC/RADIUS, CoA, guest — see
   [[nac-guest-coa]]) still functions. Re-run the render gate on affected templates; alarms 0-new on both.

6. **Decommission the source** (only after the target is verified good) per Human-Authority approval; keep
   the baseline export as the rollback point.

## Verify (do not skip)

- Every device now appears in the **target** org inventory (by id/MAC), on the correct site_id, and is gone
  from the source.
- Moved devices render the cloned templates (render gate clean) and interop dependencies pass.
- No new alarms on either org attributable to the migration.
- Source/target addressed by **ID** throughout; revert manifest complete.

## Do NOT

- Do not address orgs/sites by name at any step.
- Do not release devices before the target is cloned + ready to claim (bounded downtime).
- Do not put claim/activation codes or secrets in chat or git.
- Do not write either org without Human-Authority approval, a change window, and a tested rollback.
- Do not fold real customer org IDs/identifiers into any shared copy of this runbook ([[sanitization-gate]]).
