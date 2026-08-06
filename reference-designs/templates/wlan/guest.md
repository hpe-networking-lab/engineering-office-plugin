# WLAN Template — Guest (captive portal, isolated)

**Use for:** visitor/public access. Isolated from corporate; internet-only.

## Best-practice settings
- **Security:** open **only with a captive portal** (Mist guest portal or external), or WPA3
  with a rotating/sponsored PSK. Never a bare open SSID.
- **Isolation:** dedicated guest VLAN, **client isolation on**, no east-west to corporate.
  **Broadcast limit on**, ARP filter on.
- **VLAN:** dedicated guest VLAN (not 1). Guest subnet uses its own gateway/DHCP/DNS,
  firewalled to internet-only.
- **Portal:** click-through, sponsored, or credentialed; set session duration and re-auth.
- **Rate limiting:** per-client up/down caps as appropriate.
- **Band steering:** on. **mDNS:** off (no cross-service discovery for guests).

## Mist API payload skeleton
```json
{
  "ssid": "DAL_GUEST",
  "enabled": true,
  "auth": { "type": "open" },
  "portal": {
    "enabled": true,
    "auth": "none",              
    "sponsor_enabled": false,
    "session_expiry": 480         
  },
  "isolation": true,
  "limit_bcast": true,
  "arp_filter": true,
  "vlan_enabled": true, "vlan_id": 900,
  "band_steer": true,
  "ratelimit": { "enabled": true, "wxtag_ids": [] }
}
```
> `portal.auth` options include `none` (click-through), `sponsor`, `sms`, `email`, `external`.
> For an external portal, set `portal.auth: "external"` and the redirect URL as a site
> variable so it can point at a local server per site.

## Validation
- Audits clean (no open SSID without portal, broadcast/ARP controls on, isolation on).
- Test: guest associates → redirected to portal → internet-only, no corporate reachability.
