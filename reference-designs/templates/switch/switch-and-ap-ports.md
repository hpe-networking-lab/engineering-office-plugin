# Switch Template + AP Port Profiles (Mist Wired)

**Principle:** manage switches **through Mist, not CLI**. Push config from an **org-level
network template**; keep site/device to genuine local values via **site variables**.

## AP access port profile (switch port an AP plugs into)
- **Trunk:** tagged SSID/data VLANs + **untagged native = AP management VLAN** (e.g. 312).
- **PoE on** (AP47 = 802.3bt-capable; ensure budget). **LLDP on** for power negotiation.
- **No port security / MAC limit** on AP ports (unless *all* WLANs are bridged).
- **No 802.1X** on the AP uplink port itself. **BPDU guard** off on AP trunk (it's a trunk).
- Native VLAN **not** 1.

```json
// port_usage in POST /api/v1/orgs/{org_id}/networktemplates
"ap": {
  "mode": "trunk",
  "native_network": "mgmt_312",
  "networks": ["corp_217", "leap_2011", "guest_900"],
  "poe_disabled": false,
  "enable_mac_auth": false,
  "port_auth": null,
  "stp_edge": false,
  "disable_autoneg": false
}
```

## Uplink (switch-to-switch)
- **PoE OFF** on uplinks. Trunk all needed VLANs, native = mgmt. Consider LACP for redundancy.

## 802.1X access port (wired user ports, if used)
- `port_auth: "dot1x"`, RADIUS via site variables, **reauth 21600–43200 s (6–12 h)**,
  **no MAC-based match on the same port**, guest/rejected VLAN + a **restricted profile** for
  unknown devices.

## Site variables (define once, value per site)
`mgmt_vlan`, `corp_vlan`, `auth_srv1/2`, `native_vlan` — referenced by the template, resolved
per site.

## Validation
- Audits clean: no CLI-managed switches, no port security on AP ports, PoE off on uplinks,
  native ≠ VLAN 1, dot1x reauth in range, restricted profile present.
