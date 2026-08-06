---
name: config-backup
description: Capture a versioned baseline export of live config/state BEFORE any change — from whatever
  you run (Mist, Junos, ClearPass, Windows/AD, etc.). Read-only, low-risk. Use whenever you're about to
  make a change and need a diffable, reversible pre-change snapshot, or when someone asks to back up /
  export / snapshot a device or system's current state. Trigger words: baseline, backup config, export
  config, pre-change snapshot, capture current state, rollback point, diffable baseline.
---

# config-backup

> Pull and version a baseline export of live state before any change, so the change is **diffable and
> reversible**. **Read-only** — only reads; never writes to a device or system. **Self-contained +
> configurable:** it exports from *your* connectors to *your* configured location. Governing standard:
> [[eo-guardrails]] — reflex 5 (baseline before any change), reflex 1 (live is truth), reflex 4
> (secrets from your `credentials_file`). This is the first step of any change-making skill, incl.
> [[mist-template-rollout]]; its inverse is [[restore-config]].

## Read your config first

From `eo.config.yaml`: `paths.exports_dir` (where baselines are written), `paths.credentials_file`,
`paths.scripts_dir` (optional backup scripts), and the enabled `connectors`. Drive your own backup
tooling if `scripts_dir` provides it; otherwise export directly from the connectors you have.

## Guardrails carried from the standard

- **Read-only.** Export only. If a task needs a change, that's a separate, gated action — capture the
  baseline here first.
- **Secrets from your `credentials_file`.** Verify presence, never value; never print a secret. Address
  devices by their inventory ID/handle, not an ad-hoc host ([[eo-guardrails]] reflex 7).
- **Dry-run first when unsure** if your tooling supports it. **One driver** — don't race another session.

## Procedure

1. **Ground.** Confirm `credentials_file` present and target connector(s) reachable.

2. **Export the system(s)** you're about to change, read-only, into a **timestamped** directory under
   `exports_dir` (e.g. `<exports_dir>/<system>/<timestamp>/...`), updating a `latest` pointer. Capture the
   objects that matter for the change: templates/WLANs/site-settings and access/NAC objects for cloud
   networking; running/candidate config for devices; policy/enforcement/sessions for NAC; users/OUs/
   GPOs for directory.

3. **Confirm the export landed** — list the timestamped dir; verify the expected object files are present
   and non-empty. A per-object error means that source didn't answer — ground it (reachability / creds /
   service), don't read it as "nothing there."

4. **Record the baseline pointer** (the `<system>/<timestamp>/` path) in your change/engagement record so
   the later diff/rollback references an exact snapshot. For template-governed changes, this is the
   "before" that the render gate and read-back verify against.

5. **Report** the export path(s), object counts, and any error rows. This snapshot is now the revert
   reference for the change that follows ([[restore-config]]).

## Verify (do not skip)

- The timestamped export dir exists with the expected object files (non-empty).
- The `latest` pointer points at the run you just made.
- No secret value was printed anywhere.

## Do NOT

- Do not treat a backup as a change — it isn't, and must never be extended to write.
- Do not commit raw exports containing customer identifiers to a shared repo without the sanitization
  gate ([[sanitization-gate]]) + Human Authority approval.
- Do not print or log any secret value.
