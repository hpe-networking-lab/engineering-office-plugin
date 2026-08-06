---
name: onboarding-shakedown
description: Prove a freshly set-up environment actually works — end to end and READ-ONLY — before doing any
  real work. Use right after installing the bundle and standing up connectors, when someone says their
  setup is new / they just installed / they want to prove it works, or asks for a smoke test or first run.
  Runs a connector health check, a skill test, a grounding test, and one bounded read-only deliverable, then
  reports readiness. Trigger words: shakedown, first run, just installed, prove my setup, smoke test, is my
  environment working, verify setup, new engineer setup.
---

# onboarding-shakedown

> A guided, **READ-ONLY** first run that proves a new environment is wired correctly before it touches real
> work. Every step only reads; nothing writes to any tenant and nothing targets a customer. **Self-contained
> + configurable:** it exercises *your* connectors and grounds on the bundle's own reference designs.
> Governing standard: [[eo-guardrails]] — reflex 3 (ground before assert), reflex 1 (live is truth),
> reflex 8 (writes are gated). Run it after [[connector-setup]].

## Read your config first

From `eo.config.yaml`: which `connectors` are enabled and your `workspace_root`. If a connector isn't up
yet, do [[connector-setup]] first. Everything below is read-only — if a step can't run yet (no connector,
no data, no sample), say so plainly and continue; don't fake a pass.

## Procedure (report after each step; NEVER target a customer/production org)

1. **Connector smoke test.** Run a read-only cross-platform health check and list the orgs / sites /
   devices you can see. This proves the connector is up *and* your credentials resolve. Zero writes.

2. **Skill test.** `skills_list`, then `skills_load` and run a **read-only** audit skill (e.g.
   `mist-scope-audit` / `central-scope-audit` / `infrastructure-health-check`) against a **test or lab**
   org, and summarize what it found. Proves the skills library is reachable and functioning.

3. **Grounding test.** Self-ground on `reference-designs/` (the Mist template playbook, templates, interop
   designs) and [[eo-guardrails]], then state back — in one short paragraph — the gates you now follow and
   the Mist reference architecture. Proves the standard is loaded, not just installed.

4. **Bounded-deliverable test.** Offer to run a **read-only** config review against a SAMPLE or lab config
   the human provides; produce a short findings brief; then **STOP for review**. If they have no sample,
   skip it and say so. Proves the "bounded deliverable → stop at the gate" habit, not just tool access.

5. **Report readiness.** What passed, what still needs an input (a credential, a sample, a connector). Then
   hand off: from here the human directs their own work as the Human Authority. Name this chat and every
   future one WHO-FIRST per the chat-title standard ("<Customer>: <effort>" / "Lab: <effort>").

## Verify (do not skip)

- Every step was read-only; no write reached any tenant, and no customer/production org was touched.
- Each "pass" is backed by real output (orgs listed, skill findings, a grounded paragraph) — not an
  assumption that it *would* work.
- Any step that couldn't run was reported with the exact missing input, not worked around.

## Do NOT

- Do **not** target a customer or production environment in a shakedown — test/lab orgs only.
- Do **not** write to, change, or "just try" anything on a tenant; this skill is proof-by-reading.
- Do **not** declare the setup "ready" while a connector or credential is missing — name what's needed
  ([[eo-guardrails]] reflex 8; don't overclaim).
