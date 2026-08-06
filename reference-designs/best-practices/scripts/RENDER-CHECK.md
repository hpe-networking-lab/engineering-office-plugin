# Render smoke-test runbook (Mist template pages)

The definitive catch for the "schema-valid payload, UI still crashes" class (see
`best-practices/VALIDATION.md` §Consumer-render safety). Run after ANY template write, before marking
a template done and before activation.

**Gate rule:** no template is "done", and none is activated, until its page opens with a **clean
console** — no `TypeError`, no "An unexpected error occurred."

## Steps (via the Claude-in-Chrome MCP)
1. `list_template_urls.py` emits the page URL for every template in the org (below). Or build them by
   hand from the patterns in the table.
2. For each URL: `navigate` to it → `read_console_messages{onlyErrors:true, clear:true}` → open the
   object (click the row) → `read_console_messages{onlyErrors:true}` again.
3. A clean pass = **no** `TypeError` / `Cannot convert undefined or null to object` / `unexpected error`.
   On a hit, the JS stack names the renderer + field (e.g. `Object.keys()` in `makeRow`) — fix the
   named field, don't guess. `read_network_requests` shows the failing API call if needed.
4. Do a full reload (`ctrl+r`) between fixes so cached JS state doesn't mask a change.

## Page-URL patterns (org-scoped templates)
Base: `https://manage.<cloud>.mist.com/admin/?org_id=<ORG>#!<hash>` — `<cloud>` is the org's cloud
(e.g. `gc4`). Navigate to the **list** hash, then click the row (the SPA rejects deep per-object URLs).

| Template kind | How to reach it (verified 2026-07-04, GC4) |
|---|---|
| WLAN templates | list `#!templates` → click the row |
| RF templates | list `#!rftemplates` → click the row (direct: `#!rftemplates/rfTemplate/<id>`) |
| Switch templates | **Organization ▸ Wired ▸ Switch Templates** (menu). Direct: `#!switchTemplate/detail/<tplId>/<siteId>`. The plural `#!switchTemplates` hash returns a permissions page — do not use it. |
| Site config templates | **Organization ▸ Admin ▸ Site Configuration** — applied via Site settings; an unassigned sitetemplate has no standalone page |
| WLANs (org) | `#!wlans` |

> Deep per-object hashes are unreliable for some kinds (the SPA rejects them and shows a permissions
> page). When in doubt, reach the page from the **Organization** menu and click the row — that always
> works. `list_template_urls.py` emits the reliable form for each kind.

## Console-error signatures to grep (`read_console_messages` pattern)
`Cannot convert undefined or null to object|TypeError|makeRow|makeBody|unexpected error|Object\.keys`

## Notes
- The benign `L.Mixin.Events ... Deprecated include` Leaflet warning is not a failure — ignore it.
- This is read-only viewing of an already-authenticated session; it makes no writes.
