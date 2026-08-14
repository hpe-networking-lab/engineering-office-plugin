# Setup — Engineering Office Standard

This bundle is **self-contained**. It does not assume you have any particular server, lab, or repo — it
adapts to your setup through one config file. You can run it entirely on your own PC, or point it at a
shared remote. Five minutes to set up.

## 1. Install the plugin

```
/plugin marketplace add https://github.com/hpe-networking-lab/engineering-office-plugin.git
/plugin install engineering-office-plugin@engineering-office-marketplace
```

## 2. Create your config

Copy the example and fill it in:

```
cp config/eo.config.example.yaml eo.config.yaml
```

Then choose your mode.

### Option A — Local (everything on your PC)

Nothing external required. Set:

```yaml
mode: local
paths:
  workspace_root: "./eo-workspace"     # a folder on your machine for engagements/inventory/exports
  credentials_file: "./credentials.yml"  # your own gitignored secrets file (create it; never commit it)
standards_source: ""                     # leave blank — each skill carries its discipline inline
```

The skills read and write local files under `workspace_root`. Git is optional — a local repo gives you
history and the branch->review habit, but you don't need a remote. This is the fully self-contained mode.

### Option B — Remote (a shared git repo is your source of truth)

Use this if your team keeps standards/engagement state in a git remote (like the reference lab does):

```yaml
mode: remote
paths:
  workspace_root: "./eo-workspace"
  credentials_file: "./credentials.yml"
standards_source: "https://github.com/<your-org>/<your-standards>.git"   # optional but recommended
remote:
  repo_url: "https://github.com/<your-org>/<your-engagements>.git"
  default_branch: "main"
  pr_method: "web"        # or gh-cli / token
```

In remote mode the skills follow branch -> PR -> review -> merge, and (if `standards_source` is set) they
**defer to that source as authoritative** — so you inherit standards updates without re-installing the
plugin.

## 3. Point the connectors you use (optional)

If a skill touches Mist / ClearPass / ESXi / Junos / AD, enable it under `connectors:` and put the
connection details (host, token) in your `credentials_file`. Skills verify a secret's **presence, never
its value**, and never print it. Leave everything `false` if you're only using the read-only/doc skills.

Copy `.mcp.json.example` to `.mcp.json` and fill in your own MCP endpoints if you use MCP connectors.

## Coexisting with your existing MCPs

This plugin **registers no MCP automatically** — there is no active `.mcp.json` and the manifest declares
no servers, so installing it never touches connectors you already run. Connectors are opt-in
(`connectors:` in `eo.config.yaml`, all off by default). When you add one:

- **Give it a unique name** (e.g. an `-eo` suffix) so it can't shadow a connector you already have.
- **Already run a similar MCP** (your own Mist/Junos/etc.)? Either point the skills at it and don't add a
  second, or keep both and know their tools overlap — Claude may be ambiguous about which to call.
- **Spot duplicates fast:** the `onboarding-shakedown` skill's connector health check lists what's
  connected, so you see overlaps before doing real work.

## 4. Try it

Ask Claude to reconcile your inventory or capture a baseline. The relevant skill fires, reads your
`eo.config.yaml`, and operates on **your** paths/connectors — no reference-lab resources assumed.

## The two things to know about self-contained mode

- **Standalone floor.** With `standards_source` blank, each skill carries its own guardrails and
  procedure — the bundle works with nothing else installed.
- **Inherit-instead-of-drift.** If you *do* set `standards_source`, the skills treat it as authoritative
  and re-read it, so your standards stay current without re-publishing. Set it once you have a canonical
  home for your standards; until then, the inline version is the source of truth.
