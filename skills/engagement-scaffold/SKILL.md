---
name: engagement-scaffold
description: Stamp a new customer engagement workspace from a standard phase template (00_Project ..
  08_Review) with a valid project-state file and a catalog entry. Use whenever a new customer / project /
  engagement is being started and needs its standard workspace created. Trigger words: new engagement, new
  customer project, scaffold engagement, start a project, project state, stamp a new customer, onboarding
  a customer.
---

# engagement-scaffold

> Create a new engagement workspace from a canonical phase template, with a valid project-state file, so
> every engagement starts identical and to-standard. **Self-contained + configurable:** if your
> `standards_source` defines a `customer-template` and a state schema/validator, use those (authoritative);
> otherwise use the built-in default below. Governing standard: [[eo-guardrails]] — reflex 8 (Human
> Authority approves creating the engagement/repo), reflex 4 (no secrets), sanitize before sharing.

## Read your config first

From `eo.config.yaml`: `paths.workspace_root` (where engagements live), `mode` (local vs remote), and
`standards_source` (a template + validator, if you have one). New engagements are created under
`workspace_root`.

## Guardrails carried from the standard

- **Human Authority approves creation.** Creating a new engagement dir/repo (and, in remote mode, a new
  git repo) is a boundary change — confirm first; never create a public repo without approval.
- **Sanitize / no secrets.** The scaffold is a template with `PLACEHOLDER` values — never pre-fill it with
  another customer's data; never put secrets in it (reference your `credentials_file`).
- **To the standard, not improvised.** The engagement must carry the required artifact set (see
  [[engagement-doc-package]]). The scaffold creates the phase folders; deliverables come later.

## Default phase structure (the built-in template)

Create these phase folders (each with a short README describing its purpose):

```
<engagement>/
  00_Project/      Project_State.yaml + overview
  01_Discovery/    what the customer has/needs; requirements, constraints
  02_Engineering/  ADR(s) — decisions with validation
  03_HLD/          Architecture Recommendation (exec-summary first) + topology
  04_LLD/          DESIGN — components, flows, exact config, ports
  05_Mist/         cloud/template config (or your platform equivalent)
  06_Config/       device/baseline config
  07_Deployment/   what was deployed
  08_Review/       validation review to the observable effect
```

`Project_State.yaml` (fill every `PLACEHOLDER`; use real ISO dates):

```yaml
version: "0.1"
project:  {id: "PLACEHOLDER", name: "PLACEHOLDER", status: "not_started", created_at: "YYYY-MM-DD", updated_at: "YYYY-MM-DD"}
customer: {name: "PLACEHOLDER", industry: "PLACEHOLDER", primary_contact: "PLACEHOLDER"}
current_phase: "00_Project"
phases:
  - {id: "00_Project", name: "Project", status: "not_started"}
  # ... 01_Discovery .. 08_Review, all "not_started"
approval_gates: []
artifacts: []
blockers: []
audit: {created_by: "PLACEHOLDER", last_updated_by: "PLACEHOLDER", last_reviewed_by: "PLACEHOLDER"}
```

## Procedure

1. **Confirm scope with Human Authority:** customer name, a short project `id`, and where the scaffold
   lives (which path/repo). No new repo without explicit approval.
2. **Create the workspace** under `workspace_root`: if `standards_source` provides a `customer-template`,
   copy that; otherwise stamp the default structure above.
3. **Fill `00_Project/Project_State.yaml`** — replace every `PLACEHOLDER`; real dates, not `1970-01-01`.
4. **Validate** — if `standards_source` ships a validator, run it and fix every error until it passes. If
   not, self-check: all required fields present, `current_phase` valid, phase list complete, no
   `PLACEHOLDER`/`1970-01-01` remaining.
5. **Register it** — add a catalog/index entry (your projects catalog) so it's reproducible.
6. **Commit** — in remote mode via `feature/<engagement>-scaffold` → PR → review (no direct commits to the
   default branch); nothing customer-facing without Human Authority.

## Verify (do not skip)

- The state file passes your validator (or the self-check) — no `PLACEHOLDER`, no `1970-01-01`.
- The phase folders exist; the catalog entry is added.

## Do NOT

- Do not pre-populate the scaffold with another customer's data — start from `PLACEHOLDER`.
- Do not put secrets/credentials in the engagement files.
- Do not skip validation — an invalid state file breaks engagement tracking downstream.
