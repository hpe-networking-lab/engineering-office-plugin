#!/usr/bin/env python3
"""
mist_template_lint.py — pre-deploy consistency lint for Mist template payloads.

Catches the class that field-level OpenAPI validation cannot: a payload that is
schema-valid field-by-field but crashes the Mist UI because a renderer assumes a
sub-object exists whenever a sibling flag is set (e.g. dynamic_vlan.enabled with
no `vlans` map -> Object.keys(undefined) -> template page crash).

Two independent checks:
  1. OpenAPI field-validation (unknown + deprecated fields), if a spec is given.
  2. Flag-implies-sibling consistency rules (below) — always run, no spec needed.

Usage:
  # lint local payload file(s) (a WLAN object, or {"wlans":[...]}, or a list)
  python3 mist_template_lint.py payload.json [more.json ...] [--openapi mist.openapi.json]

  # lint the live WLANs of a template straight from the org (read-only GET)
  python3 mist_template_lint.py --org <ORG_ID> --template <TPL_ID> \
        --base https://api.gc4.mist.com/api/v1 --token-file /path/to/token \
        [--openapi mist.openapi.json]

Exit code 0 = clean, 1 = findings. No secrets are printed or stored.
"""
import argparse, json, sys, urllib.request, urllib.error

# ---- consistency rules: (label, predicate, requirement, why) -----------------
def _nonempty(v):
    return v not in (None, "", [], {}) 

def wlan_rules(w):
    """Yield (severity, message) for one WLAN dict."""
    ssid = w.get("ssid", "<no-ssid>")
    dv = w.get("dynamic_vlan") or {}
    if dv.get("enabled"):
        if not (_nonempty(dv.get("vlans")) or _nonempty(dv.get("default_vlan_ids"))):
            yield ("ERROR", f"{ssid}: dynamic_vlan.enabled but no `vlans` map and no "
                   f"`default_vlan_ids` -> Mist UI Object.keys(undefined) crash. "
                   f"Set vlans/default_vlan_ids, or dynamic_vlan.enabled=false.")
    dp = w.get("dynamic_psk") or {}
    if dp.get("enabled") and not _nonempty(w.get("auth_servers")):
        yield ("ERROR", f"{ssid}: dynamic_psk.enabled but no auth_servers "
               f"(dynamic PSK is RADIUS-sourced) -> invalid / UI fault.")
    auth = w.get("auth") or {}
    if auth.get("type") == "eap" and not _nonempty(w.get("auth_servers")):
        yield ("ERROR", f"{ssid}: auth.type=eap (802.1X) but no auth_servers.")
    if auth.get("type") == "psk" and not auth.get("multi_psk_only") \
            and not _nonempty(auth.get("psk")) and not dp.get("enabled"):
        yield ("WARN", f"{ssid}: auth.type=psk but no psk / multi_psk_only / dynamic_psk — "
               f"passphrase source undefined.")
    portal = w.get("portal") or {}
    if portal.get("enabled") and not any(k in portal for k in ("auth", "expire", "sms", "email")):
        yield ("WARN", f"{ssid}: portal.enabled but portal body is empty.")

# ---- OpenAPI field-validation (optional) ------------------------------------
def load_spec(path):
    spec = json.load(open(path))
    return spec.get("components", {}).get("schemas", {}) or spec.get("definitions", {})

def resolve(defs, s, d=0):
    if d > 40 or not isinstance(s, dict): return s
    if "$ref" in s: return resolve(defs, defs.get(s["$ref"].split("/")[-1], {}), d + 1)
    return s

def mprops(defs, s, d=0):
    s = resolve(defs, s, d); p = {}
    if not isinstance(s, dict): return p
    for sub in s.get("allOf", []): p.update(mprops(defs, sub, d + 1))
    p.update(s.get("properties", {}))
    return p

SKIP = {"id", "org_id", "site_id", "site_ids", "for_site", "created_time",
        "modified_time", "template_id", "mxtunnel_id", "wxtunnel_id"}

def field_validate(defs, obj, schema, path, out):
    schema = resolve(defs, schema)
    if not isinstance(obj, dict) or not isinstance(schema, dict): return
    props = mprops(defs, schema); addl = schema.get("additionalProperties", True)
    for k, v in obj.items():
        if k in SKIP: continue
        if k not in props:
            if addl is False: out.append(("ERROR", f"UNKNOWN field {path}.{k}"))
            continue
        fs = resolve(defs, props[k])
        if fs.get("deprecated") and _nonempty(v):
            out.append(("WARN", f"DEPRECATED field {path}.{k} — successor may be the only one the UI reads"))
        en = fs.get("enum")
        if en and not isinstance(v, (dict, list)) and v not in en:
            out.append(("ERROR", f"ENUM {path}.{k}={v!r} not in {en}"))
        if isinstance(v, dict):
            field_validate(defs, v, props[k], f"{path}.{k}", out)
        if isinstance(v, list):
            items = fs.get("items", {})
            for i, el in enumerate(v):
                if isinstance(el, dict):
                    field_validate(defs, el, items, f"{path}.{k}[{i}]", out)

# ---- payload harvesting -----------------------------------------------------
def wlans_from(obj):
    if isinstance(obj, list): return obj
    if isinstance(obj, dict):
        if "wlans" in obj and isinstance(obj["wlans"], list): return obj["wlans"]
        if "ssid" in obj: return [obj]
    return []

def http_get(base, token, path):
    req = urllib.request.Request(base + path, headers={"Authorization": "Token " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--openapi")
    ap.add_argument("--org"); ap.add_argument("--template")
    ap.add_argument("--base", default="https://api.mist.com/api/v1")
    ap.add_argument("--token-file")
    args = ap.parse_args()

    wlans = []
    for f in args.files:
        wlans += wlans_from(json.load(open(f)))
    if args.org and args.template and args.token_file:
        token = open(args.token_file).read().strip()
        allw = http_get(args.base, token, f"/orgs/{args.org}/wlans")
        wlans += [w for w in allw if w.get("template_id") == args.template]

    if not wlans:
        print("no WLANs found to lint (pass payload file(s) or --org/--template)"); return 0

    defs = load_spec(args.openapi) if args.openapi else None
    findings = []
    for w in wlans:
        for sev, msg in wlan_rules(w):
            findings.append((sev, msg))
        if defs is not None:
            field_validate(defs, w, defs.get("wlan", {}), w.get("ssid", "wlan"), findings)

    errs = [m for s, m in findings if s == "ERROR"]
    warns = [m for s, m in findings if s == "WARN"]
    for m in errs:  print("ERROR  " + m)
    for m in warns: print("WARN   " + m)
    print(f"\nlinted {len(wlans)} WLAN(s): {len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main())
