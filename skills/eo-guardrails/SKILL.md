---
name: eo-guardrails
description: The Engineering Office Standard engineering guardrails. Load and follow these reflexes at the
  start of any network/infrastructure engineering work and before ANY change to a device, cloud org,
  template, inventory, or repo. Use whenever the task touches Mist, Junos, ESXi, AD, ClearPass, a
  customer/production environment, secrets/credentials, a config write, a template, or a git commit/PR —
  or whenever you're about to assert a fact, deploy a change, or say a capability "doesn't exist."
  Trigger words: guardrails, operating standard, ground before assert, validate to the wire, render gate,
  one driver, reference by ID, secrets, credentials, Human Authority approval.
---

# Engineering Office Standard — Engineering Guardrails

> The durable reflexes that make engineering work safe to hand to a customer and repeatable next time.
> Tools change; these don't. **Self-contained:** these reflexes stand alone and require no particular
> server, lab, or repo. This skill is the always-on grounding for the bundle.
>
> **Where the specifics come from:** read your `eo.config.yaml` (see `SETUP.md`) for your `mode`
> (local/remote), `workspace_root`, `credentials_file`, and optional `standards_source`. **If
> `standards_source` is set, read and follow it — it is authoritative and may add or tighten rules as it
> grows** (you inherit updates without re-installing). If it's blank, the discipline below is your
> standard.

## The eight reflexes (apply on every task)

1. **Facts before assumptions; live is the source of truth.** Live state is truth; intent files are
   intent — reconcile continuously. Verify reads/writes against the object the system actually
   *consumes*, never the echo of your own write. Trust live (device/org/host state, or your reconciled
   inventory), never stale docs.

2. **Validate to the wire, not to doc-conformance.** A reproduced symptom is not a root cause. **If a
   finding implies a mature product is broadly broken, suspect your own setup first.** This one reflex is
   the difference between a demo and something you'd stake an engagement on.

3. **Ground before you assert — order of authority.** Vendor doc / reference config → the device's own
   outputs (metadata, traceoptions, stats *are* documentation) → controlled confirmation. **Never live
   trial-and-error.**

4. **Secrets discipline — your `credentials_file` only.** Secrets live only in the gitignored file named
   by `credentials_file` in your config; scripts read them at run time. Never hardcode, print, echo, or
   commit a secret, and never enter one in chat. **Verify presence, never value.**

5. **Render gate before "done" (change-making work).** A config write that returns 200 proves nothing.
   Golden object → lint → **inert deploy** → **render gate** (verify the page/state actually renders in
   the real consumer) → verify against the *consuming* object. Capture a baseline first
   ([[config-backup]]); keep a tested revert path ([[restore-config]]).

6. **One driver per environment.** Never let two sessions act on the same environment (org, device, host)
   concurrently — they collide.

7. **Reference by ID, not by name.** Orgs, sites, devices are addressed by stable **ID**, not display
   name. Names collide, get renamed, and silently point writes at the wrong object.

8. **Human Authority approves the gated actions.** Fix structural gaps quietly (a wrong assumption or
   stale-data slip is a *signal* to close a gap). Escalate only genuine approvals: destructive ops,
   credential changes, **any write to a customer/production environment**, creating a repo, force-push,
   and **anything going public**. In a lab/solo context authority is single-party; in a customer/
   production context it's two-party (they own the risk, the change window, and go/no-go).

## Change & validation gates (when the task makes a change)

- **Baseline capture first** so the change is diffable and reversible; keep a backout plan ready.
- **Inert first.** New objects created disabled / unbound; activate only on approval, one unit at a time,
  with a tested revert path. Record every created object (name + id) for a clean revert.
- **Alarms 0 → 0.** Capture environment alarms before and after a write; expect zero new alarms.
- **Source-control flow.** In **remote** mode: no direct commits to the default branch — `feature/<name>`
  → push → PR → review → merge (Human Authority holds the merge). In **local** mode: a local repo for
  history + the review habit is recommended; no remote required.
- **Review-before-public.** Any public or shared release gets a zero-tolerance sanitization scan
  ([[sanitization-gate]]) **and** explicit Human-Authority approval before it goes out. Never fold
  customer or active-engagement data into a shared artifact — sanitize first.

## Toolset awareness (before saying "can't")

Consult your configured scripts (`scripts_dir`), the connectors you've enabled, and your inventory before
declaring a capability doesn't exist. Exhaust the grounded options before escalating; document dead ends.

## The continuous-improvement loop (governance)

The practice improves every engagement **without models retraining on customer data**: deliver to the
standard → capture lessons as *proposals* → Human Authority reviews → approved improvements merge into the
standard (your `standards_source`) → the next engagement inherits the improved baseline. Because review is
mandatory, a bad lesson can't silently propagate.

## Quick self-check before you act

- [ ] About to assert a fact? → Grounded it against live / the vendor doc first.
- [ ] About to write config? → Baseline captured; built from a golden object; linted; inert; render gate
      planned; verifying against the consuming object; alarms checked.
- [ ] Touching a secret? → It comes from your `credentials_file`; verify presence, not value.
- [ ] Addressing an org/site/device? → By ID, not name.
- [ ] Anything else driving this environment right now? → If unsure, stop.
- [ ] Gated action (customer/production write, destructive op, credential change, repo, public)? → Get
      Human Authority approval first.
