# WLAN Template — Corporate 802.1X (WPA3/WPA2-Enterprise)

**Use for:** employee/corporate access with per-user identity via RADIUS (802.1X EAP).

## Best-practice settings
- **Security:** WPA3-Enterprise (fall back to WPA2-Enterprise for legacy clients; a
  transition mode may be used where mixed clients exist). Never WEP/WPA1.
- **Auth:** EAP to RADIUS. **Auth-server IPs via site variables** (`{{auth_srv1}}`,
  `{{auth_srv2}}`) — never hardcoded — so the template serves every site.
- **VLAN:** production data VLAN (e.g. 217 for DAL corp) — **never VLAN 1**. Prefer
  RADIUS-assigned VLAN (dynamic) where the NAC returns `Tunnel-Private-Group-ID`.
- **Fast roaming (802.11r):** **on** (valid because this is Enterprise).
- **Band steering:** on. **PMF/802.11w:** required for WPA3, capable for WPA2.
- **mDNS/Bonjour:** off, or scoped `same_site` only if needed. **Broadcast/ARP:** default.
- **CoA/Access Assurance:** enable RADIUS CoA (port 3799) if the NAC does dynamic
  authorization.

## Mist API payload skeleton
`POST /api/v1/orgs/{org_id}/templates` (or add the WLAN to an existing WLAN template):
```json
{
  "ssid": "DAL_AOT",
  "enabled": true,
  "auth": { "type": "eap", "pairwise": ["wpa3"], "pmf": "required" },
  "auth_servers": [
    { "host": "{{auth_srv1}}", "port": 1812 },
    { "host": "{{auth_srv2}}", "port": 1812 }
  ],
  "acct_servers": [ { "host": "{{auth_srv1}}", "port": 1813 } ],
  "auth_servers_timeout": 5,
  "coa_enabled": true, "coa_port": 3799,
  "vlan_enabled": true, "vlan_id": 217,
  "dynamic_vlan": { "enabled": true, "type": "standard", "default_vlan_id": 217 },
  "band_steer": true,
  "fast_dot11r": true,
  "hide_ssid": false
}
```
> Replace `{{auth_srv1/2}}` via **org/site variables**, not literal IPs. For dynamic VLANs,
> the NAC must return the VLAN attribute; otherwise set a static `vlan_id`.

## Validation
- Audits clean under `mist-scope-audit` (no hardcoded RADIUS IP, no VLAN 1, 11r on
  Enterprise, WPA3). Confirm EAP success + correct VLAN via a test client.
