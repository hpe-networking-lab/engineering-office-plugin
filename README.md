# Engineering Office Standard

An installable **practice bundle** that makes a proven set of engineering guardrails and runbooks the
default way Claude works. **Self-contained** — it assumes no particular server, lab, or repo, and adapts to
*your* setup through one config file. Run it entirely on your own PC, or point it at a shared remote.

It ships three things:

1. **Grounding** — a copy-paste `grounding/PROJECT-INSTRUCTIONS.md` that grounds every session, twinned
   with an always-on skill.
2. **A skills library** — guardrails + runbooks that trigger automatically.
3. **A plugin/marketplace** — bundling the above (plus a config layer + connector template) for one-click
   install.

## Self-contained by design

Every skill carries its own discipline and procedure, so the bundle works with **nothing else installed**.
Where a skill needs a location or a connector, it reads your `eo.config.yaml` (see `SETUP.md`) instead of
any hardcoded path. Two ways to run it — pick with one setting:

- **Local mode** — everything on your PC. Skills read/write local files under your `workspace_root`; git is
  optional; no server or remote required. Fully self-contained.
- **Remote mode** — a git remote is your shared source of truth. Skills follow branch → PR → review → merge.

### Avoiding standards drift (optional but recommended)

Set `standards_source` in your config to a canonical standards folder or repo, and the skills treat it as
**authoritative** — they re-read it and you inherit updates without re-installing the plugin. Leave it blank
and the discipline baked into each skill is your standard. This is how you choose between "self-contained
snapshot" and "always-current inheritance."

## What's inside

Twelve skills — always-on grounding, read-only checks, engagement/documentation, and fully-gated change
runbooks. Each encodes the guardrails, not just the happy path, and defers to your `standards_source` when
set.

| Skill | What it does | Risk |
|---|---|---|
| **eo-guardrails** | The eight always-on reflexes + change/validation gates. | grounding |
| **connector-setup** | Stand up your OWN hpe-networking MCP connector (Docker, HTTP, your creds) — checked one-command setup. | setup |
| **inventory-reconcile** | Regenerate inventory from live (your connectors) and flag drift. | read-only |
| **config-backup** | Versioned baseline export of live state before any change. | read-only |
| **restore-config** | Roll back to a captured baseline (candidate config, confirmed snapshot revert). | change, gated |
| **sanitization-gate** | Zero-tolerance scan for identifiers/secrets before any public/shared release. | gate |
| **engagement-scaffold** | Stamp a new engagement (phases 00–08) with a valid project-state file. | scaffold, gated |
| **engagement-doc-package** | Produce the required deliverable set with traceability. | docs, gated |
| **nac-guest-coa** | Guest onboarding CoA on Mist + ClearPass via the Juniper Disconnect path (udp/3799). | change, gated |
| **mist-template-rollout** | The Mist template path: golden → lint → inert → render gate → verify. | change, gated |
| **mist-org-migrate** | Consolidate one Mist org into another (clone → release/claim → interop gate), by ID. | change, gated |
| **proxmox-ml110-provision** | Bare-metal Proxmox on HPE Gen11 via iLO Redfish (worked example + method). | change, gated |

```
engineering-office-plugin/
├── .claude-plugin/{plugin.json, marketplace.json}
├── config/eo.config.example.yaml   # copy to eo.config.yaml — mode, paths, standards_source, connectors
├── grounding/PROJECT-INSTRUCTIONS.md  # portable session grounding
├── skills/<12 skills>/SKILL.md
├── .mcp.json.example                  # connector endpoints template (no secrets)
├── SETUP.md   README.md   LICENSE
```

## Install

```
/plugin marketplace add https://github.com/hpe-networking-lab/engineering-office-plugin.git
/plugin install engineering-office-plugin@engineering-office-marketplace
```

Then follow **`SETUP.md`**: copy `config/eo.config.example.yaml` → `eo.config.yaml`, choose local or
remote, point at your paths/connectors. Five minutes.

## Guardrails this bundle enforces

Facts-first / live-is-truth · validate-to-the-wire · ground-before-assert · secrets only from your
`credentials_file` (presence, never value) · render-gate before "done" · one-driver-per-environment ·
reference-by-ID-not-name · Human Authority approves the gated actions (and **anything public**). See
`skills/eo-guardrails/SKILL.md`.

## Versioning

`0.1.0`–`0.4.0` — initial skeleton through 11 skills (grounding, reconcile, backup/restore, sanitization,
engagement scaffold + docs, NAC CoA, Mist template + org-migrate, Proxmox).

`0.5.0` — **self-contained portability**: added a `config/` layer (local/remote modes, configurable paths
and connectors, optional authoritative `standards_source`) and `SETUP.md`; reworked all 11 skills and the
grounding template to read your config instead of any hardcoded location, carry their discipline inline as
a standalone floor, and defer to `standards_source` when set (inherit-not-drift). No lab/server assumed.
