---
name: inventory-reconcile
description: Reconcile your inventory FROM LIVE sources of truth (whatever you have — Mist / ESXi / AD /
  device APIs) and flag drift against your hand-maintained intent files. Read-only, low-risk. Use whenever
  someone asks to refresh/regenerate the inventory, check for drift, confirm what's actually deployed, or
  verify a device/VM/user against live. Trigger words: reconcile inventory, drift check, live inventory,
  what's deployed, refresh inventory, source of truth, does the YAML match live.
---

# inventory-reconcile

> Regenerate the live inventory from your sources of truth and surface drift. **Read-only** — never writes
> to a device, org, or host. **Self-contained + configurable:** it drives *your* tooling and connectors,
> not any fixed lab. Governing standard: [[eo-guardrails]] — reflex 1 (live is truth), reflex 7
> (reference by ID), reflex 4 (secrets from your `credentials_file`).

## Read your config first

From `eo.config.yaml`: `paths.workspace_root` (where your inventory/intent files live),
`paths.credentials_file`, `paths.scripts_dir` (optional), and the enabled `connectors`.

- If `scripts_dir` names a reconcile script, drive it (it's your reference implementation).
- If not, perform the reconcile directly against whatever `connectors` you have enabled.
- If `standards_source` defines an inventory format, follow it; otherwise use the default below.

## Guardrails carried from the standard

- **Live is the source of truth.** Your device/cloud APIs are authoritative for what's deployed; your
  hand-maintained files are *intent*. When they disagree, live wins and the delta is **drift to report**,
  not a value to "fix" by editing live.
- **Read-only.** Only GET/read from your connectors. If a drift implies a change is needed, that's a
  *separate, gated* action ([[eo-guardrails]] reflex 8).
- **Secrets from your `credentials_file`.** Verify presence, never value — never print a token/password.
- **One driver.** Don't run this while another session is actively writing the same environment.

## Procedure

1. **Ground.** Confirm your `credentials_file` is present (presence only) and the connectors you need are
   reachable. If a required credential is absent, stop and report — never prompt for secrets in chat.

2. **Collect live state** from each enabled connector (read-only): network devices (switches/APs/gateways)
   from your Mist/controller API; VM power + guest IPs from your hypervisor; users/OUs from your directory.
   Drive your `scripts_dir` reconcile script if you have one; otherwise query the connectors directly.

3. **Write the reconciled inventory** to `workspace_root` (a generated, do-not-hand-edit file). Include a
   generation timestamp and a section per source. An error in a section means that source didn't answer —
   treat it as a data-collection gap to ground (reachability / creds presence / service status), not "no
   devices."

4. **Compute drift** vs your intent files: for each device/VM/user, compare the intent value to live
   (address by **ID**, not name). List each delta explicitly.

5. **Report** concisely: counts per source, drift count, and each drift line verbatim; point to the
   generated inventory file. Exit/flag non-zero when drift is present (expected and useful, not a failure).

## Interpreting drift

Drift is a **structural-gap signal**: the fix is usually to reconcile the intent file to live (a gated
change → in remote mode, branch/PR), never to mutate live to match a stale doc.

## Verify (do not skip)

- Counts are non-zero for sources you expect to be populated.
- The drift count in your report matches the drift section of the generated inventory.
- You're reporting from the freshly generated inventory, not a cached read.

## Scheduling (optional)

This is the natural daily drift-check. If asked to run it automatically, schedule the collection step and
surface only the drift lines + counts each run.

## Do NOT

- Do not edit the generated inventory by hand — it's regenerated from live.
- Do not "resolve" drift by writing to a live device/org.
- Do not print or log any secret value.
- Do not fold customer data into a shared inventory artifact without sanitization + approval.
