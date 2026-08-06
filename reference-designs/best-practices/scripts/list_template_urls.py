#!/usr/bin/env python3
"""
list_template_urls.py — emit the Mist UI page URL for every template in an org, so the
render smoke-test (RENDER-CHECK.md) is mechanical. Read-only GETs; no secrets printed.

Routes verified 2026-07-04 on GC4. Deep per-object hashes are unreliable for some kinds
(the SPA shows a permissions page for the plural `switchTemplates` hash), so this emits the
forms that actually work: WLAN/RF via the list hash (click the row), switch via its verified
detail route (needs a site id, fetched here).

Usage:
  python3 list_template_urls.py --org <ORG_ID> --base https://api.gc4.mist.com/api/v1 \
        --token-file /path/to/token [--manage https://manage.gc4.mist.com]
"""
import argparse, json, urllib.request

def get(base, token, path):
    req = urllib.request.Request(base + path, headers={"Authorization": "Token " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--manage", help="e.g. https://manage.gc4.mist.com (else derived from --base)")
    a = ap.parse_args()
    token = open(a.token_file).read().strip()
    manage = a.manage
    if not manage:
        host = a.base.split("//", 1)[-1].split("/", 1)[0]
        manage = "https://" + (host.replace("api.", "manage.", 1) if host.startswith("api.")
                               else "manage.mist.com")
    org = a.org
    base_url = f"{manage}/admin/?org_id={org}#!"

    # a site id is needed to build the switch-template detail route
    try:
        sites = get(a.base, token, f"/orgs/{org}/sites")
        site_id = sites[0]["id"] if sites else None
    except Exception:
        site_id = None

    def emit(label, name, url, tail=""):
        print(f"{label:7} {name:28} {url}{tail}")

    # WLAN templates — list hash, click the row
    for it in (get(a.base, token, f"/orgs/{org}/templates") or []):
        emit("WLAN", it.get("name", "<no-name>"), base_url + "templates",
             f"   (click row {it.get('id')})")
    # RF templates — direct detail route works
    for it in (get(a.base, token, f"/orgs/{org}/rftemplates") or []):
        emit("RF", it.get("name", "<no-name>"), base_url + f"rftemplates/rfTemplate/{it.get('id')}")
    # Switch/network templates — verified detail route (needs a site id)
    for it in (get(a.base, token, f"/orgs/{org}/networktemplates") or []):
        if site_id:
            emit("SWITCH", it.get("name", "<no-name>"),
                 base_url + f"switchTemplate/detail/{it.get('id')}/{site_id}")
        else:
            emit("SWITCH", it.get("name", "<no-name>"),
                 "(Organization > Wired > Switch Templates > click row)")
    # Site config templates — no standalone page when unassigned
    for it in (get(a.base, token, f"/orgs/{org}/sitetemplates") or []):
        emit("SITE", it.get("name", "<no-name>"),
             "(Organization > Admin > Site Configuration — applied via Site settings)")

if __name__ == "__main__":
    main()
