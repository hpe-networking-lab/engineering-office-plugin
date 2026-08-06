# Firmware Policy + PSK Strategy

## Firmware auto-upgrade (org level)
- **Enable org-level auto-upgrade** with an **off-hours** maintenance window (e.g. 02:00–04:00
  local) — never during business hours.
- **Pilot** on a small site group before fleet-wide rollout.
- Track version tags: **LSR** (Latest Supported Release, recommended) vs **SSR** (older,
  patched). Avoid per-device firmware pins that diverge from the org policy.

```json
// org settings auto-upgrade block
"auto_upgrade": {
  "enabled": true,
  "version": "custom",
  "time_of_day": "02:00",
  "day_of_week": "sun",
  "custom_versions": {}
}
```

## PSK / MPSK strategy
- Prefer **Cloud PSK / MPSK** over a single shared static PSK.
- Every PSK record: **VLAN assignment**, **role**, an **owner/contact** (for revocation), and
  **expiration** for guests.
- **Never reuse** a passphrase across records (defeats per-device tracking).

## Validation
- Audits clean: auto-upgrade on, off-hours window, pilot group present; PSKs carry VLAN +
  expiration, none reused.
