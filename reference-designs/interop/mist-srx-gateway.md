# Interop — Mist Access + Juniper SRX Gateway (L3 / DHCP / Firewall)

Mist (and the access switches) provide L2 + wireless; the **SRX** is the L3 gateway, DHCP
server/relay, inter-VLAN routing, and firewall. Also covers 3rd-party firewalls and external
DHCP/DNS/RADIUS.

## Architecture
```
WLAN VLANs (217/2011/900) ─ trunk ─▶ SRX IRB per VLAN (the .1 gateways)
   SRX: inter-VLAN routing + zones/policies + DHCP (server or relay) + NAT to internet
```
The supplied DAL gateways (10.192.17.1, 10.193.12.1, 10.200.11.1) are **SRX IRB interfaces**.

## SRX side (concept)
- **IRB per VLAN** = the subnet gateway; place each VLAN in a **security zone**; policies
  enforce corp↔guest isolation (guest = internet-only).
- **DHCP:** SRX as server, or **DHCP relay** to Windows/Infoblox. Set option 3 (gateway),
  option 6 (**DNS 8.8.8.8 / 1.1.1.1** per the DAL scheme — confirm internal vs public intent).
- **NAT** guest/corp to internet; screen/IDP as needed.
- Lab note: SRX changes use **`commit confirmed`** (auto-revert) per lab golden rules.

## Services interop (DHCP / DNS / RADIUS)
- **RADIUS** lives on ClearPass (see `mist-clearpass-nac.md`), not the SRX.
- **DHCP/DNS** can be SRX, Windows, or Infoblox — the WLAN VLAN’s gateway just needs a relay
  or server. Keep DNS choice deliberate (corp usually **internal** DNS, not 8.8.8.8).

## Gotchas
- **Gateway/subnet must match** the VLAN plan exactly (an IRB on the wrong subnet = no
  routing). 
- **DHCP scope/relay** missing on a VLAN = clients associate but get no IP.
- **Zone policy** too tight = no internet; too loose = guest reaches corp.
- **MTU/asymmetric routing** across the SRX if multiple uplinks.

## Validate
Client on each VLAN: DHCP lease from the right scope, correct gateway/DNS, internet reachable,
corp↔guest isolation enforced (guest cannot reach corp subnets).
