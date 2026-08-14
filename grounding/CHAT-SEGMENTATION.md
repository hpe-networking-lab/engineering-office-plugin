# Engineering Office Standard — Chat Segmentation (hub-and-spoke)

> How to organize multi-effort work so each chat stays fast, focused, and self-grounding. Generic —
> assumes no particular lab or repo; locations come from your `eo.config.yaml`.

## The problem
One long chat that spans many efforts (builds, customers, infrastructure, personal) accumulates context,
drifts, and slows every turn. The fix is structural, not a bigger model: give each effort its own chat and
keep a thin hub to route between them.

## The model: one hub, many spokes
- **Hub chat = coordination only.** Governance (standards, the lessons loop), portfolio status, and
  **routing** ("which chat does this belong in?"). It does **no** deep execution.
- **Spoke chat = exactly one effort**, each self-grounding on its own grounding file — a build, a customer
  engagement, a shared infrastructure/platform, etc.
- **Routing test:** *sustained work on one effort with its own state → that effort's chat; cross-effort,
  governance, or "where does this go?" → the hub.*

## What makes it work
1. **One grounding file per effort** (an `ENGINEERING_OFFICE.md` or equivalent) the spoke reads first — its
   charter, scope, access rules, and self-ground pointers. This is what keeps a chat specific and stops
   drift. New effort → new grounding file before real work.
2. **An effort registry the hub owns** — a one-page index: each effort, its lane, its grounding-file path,
   its status. Routing becomes a lookup, not a judgment call. Template:
   `reference-designs/templates/effort-registry.md`.
3. **Platform-vs-payload boundary.** Shared infrastructure (a lab, a test bed) is itself one effort — the
   *platform*; other efforts are **tenants** that use it. Platform work (capacity, images, fixes, the
   reusable runbook) belongs to the platform effort; the specific thing being built or tested belongs to the
   tenant. Rule: *reusable across efforts → platform; specific to one effort's deliverable → that effort.*

## Guardrails (consistent with `eo-guardrails`)
- **One driver per effort** (reflex 6): a spoke never writes another effort's repo; only the hub makes
  cross-cutting edits — one coordinated actor, no drift.
- **Keep the hub singular.** Two coordinators both promoting lessons / rewriting the standard collide.
- **Each spoke self-grounds every session** on its grounding file + the standard; it does not rely on the
  hub's memory carrying over.
