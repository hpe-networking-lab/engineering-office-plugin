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
    raw/           AS-SUPPLIED customer material, byte-for-byte, never edited
      SOURCE-MANIFEST.md   one row per file: name, received, from, sha256
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
5. **Create `01_Discovery/raw/` with a `SOURCE-MANIFEST.md`** — see "Retain the source material"
   below. Empty is fine at scaffold time; the folder existing is what makes the habit cheap later.
6. **Register it** — add a catalog/index entry (your projects catalog) so it's reproducible.
7. **Commit** — in remote mode via `feature/<engagement>-scaffold` → PR → review (no direct commits to the
   default branch); nothing customer-facing without Human Authority.

## The environment must be WRITABLE and WIRED, or a session will route around it

**Every directory must be group-writable + setgid, and the repo must carry `.mcp.json`.**
`eo_stamp_effort.sh` does both and then VERIFIES by writing as the `eo` user — use it rather than
creating directories by hand.

Why (2026-09-02): the scaffold created phase directories with a default umask, so they came out
`drwxr-sr-x` — group `eo-efforts` but no group write. The session could write the repo root and
nothing inside it. **It did not stop.** It renamed `00_Project`, `01_Discovery` and `03_HLD` to
`*.perm-stale`, created new writable directories, and copied everything across — leaving two
directories each holding `DECISIONS.md` with nothing saying which was authoritative. Every effort
repo stamped before that date had the defect, and none of it was visible until the first real
dispatched session hit it.

Separately, only one of twelve repos had `.mcp.json`. A session with no corpus connector designs
from recall, which is the failure the whole grounding discipline exists to prevent.

Both are now checked daily by `check_grounding.py`. Fixing the instances was not the fix — fixing
the generator was.

## Verify (do not skip)

- The state file passes your validator (or the self-check) — no `PLACEHOLDER`, no `1970-01-01`.
- The phase folders exist; the catalog entry is added.
- `01_Discovery/raw/SOURCE-MANIFEST.md` exists.
- `.mcp.json` exists, and `sudo -u eo find <repo> -type d ! -writable` returns NOTHING.


## Retain the source material — `01_Discovery/raw/`

**Every file the customer supplies is kept, byte-for-byte, in `01_Discovery/raw/`, and recorded in
`01_Discovery/raw/SOURCE-MANIFEST.md` with a sha256.** Configs, exports, CSVs, packet captures,
screenshots, spreadsheets. Unedited: parse into a separate artefact, never over the original.

**Use the existing convention — `SOURCE-MANIFEST.md`.** Tarrant County F2026149 is the reference
example (`tarrant-county/01_Discovery/raw/SOURCE-MANIFEST.md`); copy its shape rather than
inventing a second name for the same thing. It also handles the case where the binaries are too
large or sensitive for the repo: keep them in the local engagement workspace and record the path
in the manifest. The manifest stays in the repo either way.

```
| File | Received | From | SHA256 |
|---|---|---|---|
| coa-conductor-2026-08-28.cfg | 2026-08-28 | <contact> | 70f4945e... |

Customer data — local-only. Never GitHub, never Syncthing.
```

**Why (2026-09-01, City of Arlington):** a security finding was written from three controller
configurations supplied on 2026-08-28. Those files were not retained. The finding now carries
*"those files are no longer held in the engagement, so this has not been re-verified against its
source since"* — every conclusion drawn from them became unfalsifiable, and a later contradiction
in the record (AP-555 described as both Wi-Fi 6 and 6E) could not be settled by re-reading the
source. It took a live device query instead, which is not always available and is never available
after a customer decommissions kit.

**The rule this encodes:** a finding is only as durable as its source. A parse is a *claim about*
a file; without the file the claim cannot be checked, only believed. Keeping the raw material is
what makes "verify against the authoritative source" possible six weeks later.

Practical notes:

- **Ingest on the box, not in a chat.** A 40,000-line config that passes through a conversation is
  gone when the conversation ends and burns the context needed to think about it. Parse it where it
  lands, cite the artefact.
- **`raw/` is customer data.** It stays in the local-only engagement repo and never reaches a public
  remote — run `sanitization-gate` before anything leaves.
- **If a file cannot be retained** (licensing, customer instruction, size), say so in `SOURCE-MANIFEST.md`
  explicitly with the reason. An intentional gap that is recorded is workable; a silent one is not.
- **Record the sha256 even for files you cannot keep** — it lets a re-supplied copy be proven
  identical to the one the finding was written from.

## Do NOT

- Do not pre-populate the scaffold with another customer's data — start from `PLACEHOLDER`.
- Do not put secrets/credentials in the engagement files.
- Do not skip validation — an invalid state file breaks engagement tracking downstream.
- Do not write a finding from a file you did not retain. If the source is gone, the finding must say
  so where a reader will see it, not in a footnote.
