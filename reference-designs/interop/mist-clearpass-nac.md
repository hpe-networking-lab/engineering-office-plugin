# Interop — Mist WLAN + Aruba ClearPass (NAC / RADIUS)

Mist provides the wireless edge; ClearPass is the RADIUS/NAC brain (802.1X + MAC auth,
role/VLAN assignment, posture, guest). This is the most common cross-vendor case.

## Architecture
```
Client ──802.1X/EAP──▶ Mist AP ──RADIUS(1812/1813)──▶ ClearPass
                                 ◀──CoA(3799)─────────┘   (dynamic authz / bounce)
ClearPass returns: Access-Accept + VLAN (Tunnel-Private-Group-ID) + Role (Filter-Id / Aruba-User-Role)
```

## ClearPass side
- Add the **Mist APs (or the org’s NAS)** as **Network Devices** with a **shared secret** and
  vendor **RADIUS (IETF) / Aruba** dictionaries. NAS source is the AP’s IP (or the Mist proxy
  IP if using Mist Edge/proxy).
- **Service:** 802.1X Wireless — auth method EAP-TLS/PEAP; auth source AD / cert store.
- **Enforcement:** return **`Tunnel-Type=VLAN`, `Tunnel-Medium-Type=802`,
  `Tunnel-Private-Group-Id=<vlan>`** for dynamic VLAN; role via **`Filter-Id`** (Mist reads
  Filter-Id as the user role/GBP label).
- **CoA:** enable RFC 3576 on **UDP 3799** toward the AP/NAS for Access Assurance-style bounce.
- MAC auth service for headless/IoT (MAC format must match — see gotchas).

## Mist side
- WLAN `auth.type = eap` (see `templates/wlan/corp-dot1x.md`), **auth/acct servers =
  ClearPass** (via site variables), **CoA enabled (3799)**.
- `dynamic_vlan.enabled = true` so the RADIUS VLAN attribute is honored.
- Add ClearPass as the org/site RADIUS via **site variables** `{{auth_srv1/2}}`.
- (Alternative: Mist **Access Assurance** is Mist’s own NAC — use *either* Mist AA *or*
  ClearPass for a given SSID, not both.)

## Gotchas
- **Shared secret + NAS-IP must match exactly** on both sides — #1 failure.
- **MAC format:** align ClearPass’s expected format with what Mist sends (lowercase, colon vs
  dash) or MAC-auth silently fails.
- **CoA port:** Mist expects **3799**; some ClearPass configs default elsewhere.
- **Filter-Id vs VSA:** Mist reads standard `Filter-Id` for role; don’t rely on Aruba VSAs the
  AP won’t parse.
- **Cert trust** for EAP-TLS: clients must trust the ClearPass server cert chain.
- If using a **RADIUS proxy** (Mist Edge), the NAS-IP ClearPass sees is the proxy, not the AP.

## Validate
Test client → `mist_search_org_wireless_clients` shows EAP success + assigned VLAN/role;
ClearPass Access Tracker shows Accept with the returned attributes; CoA bounce moves the
client. On failure, check secret/NAS-IP, MAC format, and cert trust first.
