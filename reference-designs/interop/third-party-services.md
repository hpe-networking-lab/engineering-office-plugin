# Interop — Third-Party RADIUS / DHCP / DNS

Mist consumes standard network services; they don't have to be Juniper. This covers plugging
non-Mist RADIUS, DHCP, and DNS into a Mist deployment.

## RADIUS (Windows NPS / FreeRADIUS / Cisco ISE)
- Same contract as ClearPass (`interop/mist-clearpass-nac.md`): add the Mist NAS with a
  **shared secret + NAS-IP**, return **`Tunnel-Private-Group-Id`** (VLAN) and **`Filter-Id`**
  (role), enable **CoA on 3799** if doing dynamic authz.
- Mist WLAN: `auth.type=eap`, `auth_servers`/`acct_servers` = the RADIUS (via site variables),
  `coa_enabled=true`, `coa_port=3799`.
- **NPS gotcha:** NPS uses `Tunnel-*` attributes for VLAN; make sure the connection-request +
  network policies return them and that the AP IP is a registered RADIUS client.

## DHCP (Windows / Infoblox / Kea / SRX)
- The **WLAN VLAN's gateway** (SRX IRB, core switch SVI, or firewall) either **is** the DHCP
  server or **relays** (IP helper) to the DHCP host.
- Scope per VLAN: gateway (opt 3), DNS (opt 6), lease time, and any vendor options.
- **Gotcha:** a VLAN with no scope/relay = clients associate but get no IP (looks like a
  "Wi-Fi problem" but it's DHCP). Mist Marvis/`mist_get_site_sle_summary` will flag DHCP fail.

## DNS (internal AD/Infoblox vs public)
- Set DNS in the **DHCP scope**, not the WLAN. Corporate SSIDs should use **internal DNS**
  (AD/Infoblox) for name resolution + policy; guest can use public (8.8.8.8/1.1.1.1).
- **Gotcha (DAL scheme):** the supplied plan points corp at 8.8.8.8/1.1.1.1 — public DNS on a
  corp SSID usually breaks internal name resolution and AD domain services. Confirm intent;
  likely should be internal DNS for corp, public only for guest.

## Validate
Per VLAN: client gets a lease from the right scope, correct gateway + DNS, resolves an
internal name on corp (public-only on guest), reaches the internet. Marvis SLE confirms
DHCP/DNS/RADIUS success rates.
