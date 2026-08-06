# Interop — Mist + Aruba AOS / Central

Two common shapes: (1) **Mist wireless over Aruba-Central-managed wired**, and (2)
**coexistence during a migration** (Aruba APs/switches alongside Mist). Aruba Central manages
Aruba gear; Mist manages Juniper — they meet at VLANs, RADIUS, and roaming.

## Shape 1 — Mist APs on Central-managed Aruba CX switches
- Same AP-port contract as any non-Juniper switch (`interop/mist-nonjuniper-switch.md`): trunk
  tagged SSID VLANs + untagged native = AP mgmt VLAN, PoE on, LLDP on, no port-security/dot1x
  on the AP port.
- Push the port profile from **Central** (its own template model); Mist won't see the switch
  in Wired Assurance. Keep the intended port config recorded here per site.
- **Shared NAC:** point both Mist WLANs and Aruba wired 802.1X at the **same RADIUS/ClearPass**
  so identity and VLAN/role assignment are consistent across vendors.

## Shape 2 — Coexistence / migration
- During AOS→Central or Aruba→Mist transitions, run SSIDs on both vendors briefly. Keep
  **SSID name + security + VLAN identical** on both so clients roam without re-auth surprises
  (note: seamless 802.11r fast-roam does **not** cross vendors — expect full re-auth at the
  boundary).
- Use one RADIUS source of truth; avoid divergent VLAN/role policy.
- The bundled **`aos-migration`** and **`central-scope-audit`** skills cover the Aruba side
  (AOS 8→10 readiness, Central config audit) — use them for the Aruba half.

## Gotchas
- **VLAN IDs must match** across Mist, Central, and the L3 gateway.
- **Cross-vendor fast roaming** (11r/OKC) won't work between a Mist AP and an Aruba AP — plan
  for re-auth at coverage seams.
- Two management planes: don't try to manage Aruba gear from Mist or vice versa.
- Firmware/PoE budgets differ per vendor switch — verify BT support for the AP models.

## Validate
Client roams across the vendor boundary and re-auths cleanly; RADIUS (ClearPass/AA) shows the
same role/VLAN result regardless of which vendor's AP served it.
