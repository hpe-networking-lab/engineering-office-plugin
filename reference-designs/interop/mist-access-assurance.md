# Interop — Mist Access Assurance (Mist-native NAC)

Mist's **own** NAC — the alternative to an external RADIUS/ClearPass. Use **Access Assurance
(AA) OR** an external RADIUS for a given SSID, **never both**. AA suits an all-Juniper shop or
where you don't want to run a separate NAC.

## What it replaces
- The external RADIUS server: AA is Mist Cloud RADIUS with its own **PKI** (issues/validates
  client + server certs) and **auth policies**, integrated to an **IdP** (Entra ID, Okta,
  Google, or AD via LDAP) for user/group lookup.

## Mist side
- WLAN: `auth.type = eap` **plus `mist_nac.enabled = true`** (confirmed live field) — this
  points the SSID at Mist AA instead of external `auth_servers`.
- **Auth policies** (Org > Access Assurance): match on cert/user/group/device → assign **VLAN
  + role**. EAP-TLS (cert) is preferred; EAP-TTLS/PEAP for password.
- **PKI:** use Mist's built-in CA or import your own; clients enroll via MDM/SCEP or Mist
  onboarding SSID.
- **IdP:** connect Entra/Okta/AD; group membership drives the policy result.

```json
// WLAN delta vs corp-dot1x: use Mist AA instead of external RADIUS
{ "ssid": "CORP-AA", "enabled": true,
  "auth": { "type": "eap", "pairwise": ["wpa3"], "pmf": "required" },
  "mist_nac": { "enabled": true },
  "vlan_enabled": true, "dynamic_vlan": { "enabled": true, "type": "standard" } }
```

## Gotchas
- **Don't set external `auth_servers` when `mist_nac.enabled=true`** — pick one auth brain.
- EAP-TLS needs the client to **trust Mist's server cert** and hold a **valid client cert** —
  cert lifecycle (enrollment, expiry) is the main operational cost.
- IdP group→policy mapping must exist or clients get the default/denied result.
- CoA/bounce is handled by Mist internally (no external 3799 config).

## Validate (lab: CORP-AA)
Test client (the lab MacBook endpoint) → `mist_search_org_wireless_clients` shows AA auth
success, cert identity, and the policy-assigned VLAN/role. Failures: check cert trust, IdP
group mapping, and that no external RADIUS is also set.
