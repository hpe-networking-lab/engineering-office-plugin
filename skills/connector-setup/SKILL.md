---
name: connector-setup
description: Stand up YOUR OWN hpe-networking MCP connector on your machine — against your own orgs and
  credentials, pointing at nothing shared. Use when setting up the plugin for the first time, when a skill
  needs a connector that isn't running yet, or when someone asks how to connect Mist / Aruba Central /
  GreenLake / ClearPass / Apstra / AOS8 / Axis. Guides a checked, one-command Docker standup and registers
  the endpoint. Trigger words: connect, connector, MCP setup, stand up the connector, docker compose up,
  hpe-networking-mcp, Mist connector, Central connector, first-run setup, endpoint.
---

# connector-setup

> Get the hpe-networking MCP running **on your machine, against your own orgs and credentials**. The
> connector is an **HTTP service** (a container that binds a port) — there is no stdio mode, so an install
> cannot spawn it for you: it needs Docker running and your own secret files mounted. This skill makes that
> a checked, one-command standup and nothing here points at anyone else's lab, org, or credentials.
> **Self-contained + configurable:** everything runs locally and reads *your* config. Governing standard:
> [[eo-guardrails]] — reflex 4 (secrets from your `credentials_file`, presence-never-value), reflex 8
> (writes are gated), reflex 7 (address orgs/devices by ID). Pairs with the read-only smoke test in your
> onboarding shakedown.

## What you're standing up (the launch model)

- **Image:** `ghcr.io/nowireless4u/hpe-networking-mcp:latest` (public, MIT; amd64 + arm64).
- **Transport:** HTTP only. It binds `MCP_HOST:MCP_PORT` (default `0.0.0.0:8000`) — confirmed from the
  image's own `--help` (`--host` / `--port`, no stdio). So it runs as a **persistent container**, and your
  client connects to its **URL**, e.g. `http://localhost:8000/mcp`.
- **Credentials:** per-platform **secret files** mounted into the container (e.g. `mist_api_token`,
  `mist_host`, `central_client_id`, `central_client_secret`, `greenlake_*`, `clearpass_*`). Nothing inline;
  nothing committed.
- **Writes are opt-in and OFF by default:** each platform has an `ENABLE_<PLATFORM>_WRITE_TOOLS` flag
  (default `false` = read-only). Leave them false unless you own the risk on that environment.

## Read your config first

From `eo.config.yaml`: which `connectors` you've enabled, and `paths.credentials_file` (where your secret
values live). This skill verifies a secret's **presence, never its value**, and never prints one.

## Prerequisites (check, don't assume)

1. **Docker + docker-compose** present and the daemon running (`docker version`, `docker compose version`).
   If missing, that's the one thing you install yourself — a plugin can't provision a runtime.
2. Network reach from your machine to *your* platform APIs (your Mist cloud, your Central, etc.).

## Procedure

1. **Get the connector's compose + secrets layout from its own public repo** (`nowireless4u/hpe-networking-mcp`)
   — that project ships the `docker-compose.yml` and a `secrets/` template. Don't hand-copy another
   engineer's compose; start from the upstream one so you inherit its current shape.

2. **Fill only the secret files for the platforms you use.** Put each platform's values in its secret file
   (Mist token + host, Central base-url/client-id/client-secret, GreenLake ids + workspace, ClearPass, etc.).
   Delete the secret lines for platforms you don't use. Values come from *your* `credentials_file` /
   platform consoles — **presence, never value; never commit, never paste in chat** ([[eo-guardrails]] r4).

3. **Keep writes off unless you own the risk.** Leave every `ENABLE_*_WRITE_TOOLS` at `false` for a
   read-only connector. Enable a write flag only for an environment you're authorized to change
   ([[eo-guardrails]] r8) — never for a customer/production org without approval.

4. **Bring it up:** from the compose directory, `docker compose up -d`. It's a long-lived service; it stays
   up until you stop it.

5. **Verify it's live** (do this before registering): `docker compose ps` shows the container healthy, and
   the port answers — `curl -fsS http://localhost:8000/mcp` (or your `MCP_PORT`) returns without a
   connection error. If it doesn't come up, read the container logs (`docker compose logs`) — a missing or
   misnamed secret file is the usual cause; ground it, don't guess.

6. **Register the endpoint with your client.** Add an MCP connector pointing at `http://localhost:8000/mcp`
   (adjust host/port if you changed them). Copy the shape from `.mcp.json.example` in this bundle — fill in
   your real URL. Claude Desktop has no native streamable-HTTP support, so if that's your client, bridge
   stdio↔HTTP with `npx supergateway` (Cowork / Claude Code connect to the HTTP URL directly).

7. **Prove it with a read-only call.** Run a health check / `skills_list`, and list the orgs/sites you can
   see. This confirms the connector is up **and** that your credentials resolve — without changing anything.

## Verify (do not skip)

- Container is healthy and the port answers locally.
- A read-only connector call returns your own orgs/sites (proves creds resolve).
- Every `ENABLE_*_WRITE_TOOLS` is `false` unless you deliberately enabled one for an environment you own.
- No secret value was printed, committed, or pasted anywhere; your filled `.mcp.json` and secret files are
  gitignored.

## Do NOT

- Do **not** point at, reuse, or copy anyone else's running connector, endpoint, or secret files — each
  engineer runs their own, against their own orgs.
- Do **not** commit `.mcp.json`, `credentials.yml`, or any secret file (all gitignored — keep it that way).
- Do **not** enable write tools on a customer/production org, ever, without Human-Authority approval
  ([[eo-guardrails]] r8).
- Do **not** conclude "the connector is broken" from one failed call — check the container logs and secret
  presence first ([[eo-guardrails]] r2).
