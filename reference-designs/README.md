# Mist Reference Designs

A lean, best-practice **template library and interop playbook** for the Juniper Mist stack.
It is the reusable "what to build": vetted Mist building blocks (WLAN / RF / switch / site /
firmware / PSK) with the best-practice rationale behind each, plus a cross-vendor interop
playbook for when Mist meets another vendor.

This library is **vendor-design, not customer-delivery.** A customer engagement (run through
ACEDP) *consumes* these templates to produce a customer-specific design; this repo defines
the templates themselves so every deployment starts from the same vetted baseline.

## How to use

1. Pick the building blocks that match the deployment (e.g. `corp-dot1x` + `guest` +
   `iot-mpsk` WLANs, an RF baseline, the AP-port profile, a site template).
2. Apply the documented best-practice settings; each block carries the rationale and the
   Mist API payload skeleton you'd POST to create it.
3. For any non-Juniper element (NAC, switch, gateway), use the matching `interop/` playbook.
4. Validate against the `mist-scope-audit` runbook — this library and that audit share the
   same best-practice source, so a compliant deployment audits clean.

## Anchoring

Best practices are anchored on the **Juniper Mist best-practices doc**, the **Mist Wired &
Wireless Assurance Configuration Guides**, and the **AI-Driven Wired & Wireless Deployment
Guide** — the same sources the `mist-scope-audit` skill enforces.

## Index

| Area | Files |
|------|-------|
| Principles | `best-practices/PRINCIPLES.md` |
| Audit alignment | `best-practices/AUDIT_ALIGNMENT.md` |
| Payload validation | `best-practices/VALIDATION.md` |
| WLAN templates | `templates/wlan/{corp-dot1x, guest, iot-mpsk}.md` |
| RF templates | `templates/rf/rf-templates.md` |
| Switch / AP ports | `templates/switch/switch-and-ap-ports.md` |
| Switch stacking (VC) | `templates/switch/virtual-chassis.md` |
| Site baseline | `templates/site/standard-site-template.md` |
| Firmware & PSK | `templates/ops/firmware-and-psk.md` |
| Interop | `interop/README.md` + `interop/mist-*.md` |

> **Scope note:** every payload skeleton here is a *design reference*. Applying it to a real
> org is a deliberate, approved action — never write to a customer org without sign-off.
