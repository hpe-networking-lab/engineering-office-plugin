# WLAN Template — IoT / MPSK (per-device keys)

**Use for:** IoT, AV, printers, managed endpoints that can't do 802.1X — per-device unique
passphrase with per-device VLAN/role.

## Best-practice settings
- **Security:** WPA2/WPA3-Personal with **Multi-PSK (MPSK) / Cloud PSK** — a unique
  passphrase per device, **not** one shared static PSK.
- **Per-device segmentation:** each PSK record carries a **VLAN** (and role) so devices land
  in the right segment automatically.
- **ARP filter on**, broadcast limit on (IoT is chatty). **Band steering** as appropriate
  (many IoT are 2.4 GHz-only — do not force-steer those).
- **11r:** off (personal SSID — 11r requires Enterprise).
- **Lifecycle:** PSK records get owners and, where relevant, expiration; never reuse a
  passphrase across records.

## Mist API payload skeletons
WLAN:
```json
{
  "ssid": "DAL_IOT",
  "enabled": true,
  "auth": { "type": "psk", "enable_mac_auth": false },
  "dynamic_psk": { "enabled": true },
  "vlan_enabled": true, "vlan_id": 2011,
  "arp_filter": true, "limit_bcast": true,
  "band_steer": false, "fast_dot11r": false
}
```
Per-device Cloud PSK: `POST /api/v1/orgs/{org_id}/psks`
```json
{ "name": "hvac-lobby-01", "passphrase": "<unique>", "ssid": "DAL_IOT",
  "vlan_id": 2011, "usage": "single", "mac": "", "role": "iot" }
```
> Set `multi_psk_only: true` so the SSID accepts only MPSK entries. Assign VLAN in the PSK
> record for per-device placement.

## Validation
- Audits clean (MPSK over static PSK, VLAN per record, ARP filter on).
- Test: two devices with different PSKs land on their assigned VLANs.
