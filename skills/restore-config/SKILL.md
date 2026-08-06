---
name: restore-config
description: Roll back / restore from a captured baseline — device config (candidate only, never
  auto-commit), VM snapshots (confirmed revert), and versioned history. Use whenever a change needs to be
  reverted, a device/VM restored to a known-good baseline, or a milestone rolled back. The gated companion
  to config-backup. Trigger words: restore, roll back, revert, backout, undo the change, restore baseline,
  revert snapshot, rollback config, known-good.
---

# restore-config

> Restore to a captured baseline — the **backout half** of the change loop, and fully gated. Companion to
> [[config-backup]] (which captures the baseline this restores from). **Self-contained + configurable:**
> operates on *your* `exports_dir` baselines and *your* connectors. Governing standard: [[eo-guardrails]]
> — reflex 8 (Human Authority approves; revert is destructive-adjacent), reflex 5 (baseline + tested
> revert path), reflex 1 (verify against the consuming object), reflex 4 (secrets from `credentials_file`).

## Read your config first

From `eo.config.yaml`: `paths.exports_dir` (baselines to restore from), `paths.credentials_file`,
`paths.scripts_dir` (optional restore tooling), enabled `connectors`. Drive your own restore tooling if
present; otherwise apply the baseline through the connector, following the guardrails below.

## Guardrails carried from the standard

- **Revert is a change — Human Authority approves.** Solo/lab: single-party. Customer/production: their
  change approval + window + this as the documented rollback. Never revert a customer environment without
  approval.
- **Device config: candidate, not auto-commit.** Stage the historical config from the baseline as a
  **candidate**; a human reviews the diff and commits (commit-confirmed, so a bad rollback is itself
  reversible). Never blind-push a rollback.
- **VM/snapshot revert is destructive — confirm explicitly.** Reverting a snapshot discards state since
  the snapshot. Confirm the exact VM + snapshot; require an explicit confirmation step. An object with no
  matching baseline/snapshot is **skipped**, not guessed.
- **One driver.** Never revert while another session is writing the same environment. Secrets from
  `credentials_file`; presence, never value.

## Procedure

1. **Identify the baseline** (read-only first): locate the exact `<exports_dir>/<system>/<timestamp>/`
   (or snapshot) you intend to restore, and confirm it covers what you're reverting.

2. **Diff before restore.** Compare current live state to the baseline so the rollback is a known,
   reviewed delta — never a blind overwrite.

3. **Device config — stage the candidate (no commit).** Load the historical config as a candidate; review
   the diff on the device; commit with **commit-confirmed** (auto-rollback if not confirmed) — a human
   step.

4. **VM / snapshot — confirmed revert (on approval).** Revert only the named object(s), only after Human-
   Authority approval and confirming the exact target + point-in-time.

5. **Verify against the consuming object.** Confirm the device/VM is actually in the baseline state the
   system consumes (not just that the command returned) — re-read live, check render/interop where
   relevant, confirm alarms back to baseline.

6. **Record** what was restored (baseline id, targets, who approved). Capture the pre-restore state as a
   new baseline ([[config-backup]]) so the restore is itself reversible.

## Verify (do not skip)

- The baseline/snapshot you restored from is the intended one.
- Device: change landed via reviewed candidate + commit-confirmed, not a blind push.
- VM: only the named target(s) reverted; targets without a matching baseline were skipped, not guessed.
- Post-restore live state matches the baseline against the consuming object; alarms back to baseline.

## Do NOT

- Do not auto-commit a device rollback — stage the candidate, review, commit-confirmed.
- Do not revert a VM/snapshot without an explicit confirmation step **and** Human-Authority approval.
- Do not restore a customer/production environment without their change approval, window, and this as the
  rollback.
- Do not print or log any secret value.
