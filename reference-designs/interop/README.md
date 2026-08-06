# Interop Playbook — Mist + Another Vendor

When the deployment isn't all-Juniper, use these. Each playbook gives the architecture, the
config on **both** sides, the gotchas, and how to validate.

## Matrix

| Scenario | Mist role | Other vendor | Playbook |
|----------|-----------|--------------|----------|
| **NAC / RADIUS** | WLAN 802.1X + MAC auth | Aruba **ClearPass** | `mist-clearpass-nac.md` |
| **NAC (Mist-native)** | WLAN 802.1X | Mist **Access Assurance** | `mist-access-assurance.md` |
| **Aruba AOS / Central** | Mist wireless / migration | Aruba Central, AOS | `aos-central.md` |
| **Wired uplink** | APs / edge | **Non-Juniper switch** (Aruba CX, Cisco) | `mist-nonjuniper-switch.md` |
| **L3 gateway / DHCP / firewall** | Wireless + wired access | Juniper **SRX** (or 3rd-party FW) | `mist-srx-gateway.md` |
| **DHCP / DNS / RADIUS services** | consumer | Windows / Infoblox / FreeRADIUS | `third-party-services.md` |

## Golden interop rules
- **Identity is the seam.** Most interop is RADIUS: agree on shared secret, NAS-IP, MAC
  format, VLAN/role attributes, and CoA (3799) before anything else.
- **VLANs must line up end to end** — same IDs on Mist WLAN, the switch trunk, and the L3
  gateway. Mismatched native VLAN is the #1 AP-adoption failure.
- **Let each vendor own its layer**; don't double-configure the same policy in two places.
- **Validate with a real client** on each path (auth → VLAN → DHCP → DNS → gateway → internet).
