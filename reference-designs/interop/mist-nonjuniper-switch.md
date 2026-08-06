# Interop — Mist APs on a Non-Juniper Switch (Aruba CX / Cisco)

When the access switch isn’t Mist-managed (Aruba CX, Cisco Catalyst, etc.), the AP still
works — you just hand-configure the switch port to the same contract a Mist template would.

## The AP port contract
- **Mode:** trunk (802.1Q).
- **Tagged:** all SSID/data VLANs (e.g. 217 corp, 2011 leap, 900 guest).
- **Native/untagged:** the **AP management VLAN** (e.g. 312) — the AP gets its IP/adoption
  here. **Native must match** what the AP expects or adoption fails.
- **PoE:** on, **802.3bt** budget for AP47-class radios. **LLDP/LLDP-MED** on for power.
- **No port-security / sticky-MAC**, **no 802.1X** on the AP uplink port.
- MTU ≥ 1500 (higher if tunneling).

## Aruba CX example
```
interface 1/1/10
  description "Mist AP47"
  no shutdown
  vlan trunk native 312
  vlan trunk allowed 217,900,2011
  lldp mode txrx
  poe
```

## Cisco IOS-XE example
```
interface GigabitEthernet1/0/10
 description Mist AP47
 switchport mode trunk
 switchport trunk native vlan 312
 switchport trunk allowed vlan 217,900,2011
 power inline auto
 lldp transmit
 lldp receive
 spanning-tree portfast trunk
```

## Uplinks between the non-Juniper switch and the core
- Trunk the same VLANs; **PoE off**; native = mgmt; LACP for redundancy.

## Gotchas
- **Native VLAN mismatch** = AP won’t adopt (most common). 
- **PoE budget:** BT radios can exceed a switch’s per-port/global PoE budget.
- **VLAN not allowed on the trunk** = SSID associates but no DHCP.
- Since Mist doesn’t manage this switch, it **won’t appear in Wired Assurance** — document the
  port config out-of-band and keep it in this repo per site.

## Validate
AP shows connected in Mist; a client on each SSID gets DHCP on the right subnet; check the
switch’s LLDP neighbor + PoE draw.
