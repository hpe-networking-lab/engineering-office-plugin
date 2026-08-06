# Standard Site Template

Applied at **new-site creation** so every site starts from the same baseline. Reduces
per-site drift.

## Contents
- **Timezone** and **country code** (regulatory — drives allowed channels/power).
- **Firmware auto-upgrade** defaults (see `ops/firmware-and-psk.md`).
- **Default RF template** reference (Indoor-Baseline).
- **Default WLAN template** reference.
- **Site variables** pre-declared (so template pushes resolve): `mgmt_vlan`, `corp_vlan`,
  `auth_srv1`, `auth_srv2`, guest portal URL.

## Mist API skeleton
`POST /api/v1/orgs/{org_id}/sitetemplates`
```json
{
  "name": "Standard-Campus",
  "timezone": "US/Central",
  "country_code": "US",
  "rftemplate_id": "<Indoor-Baseline id>",
  "networktemplate_id": "<switch template id>",
  "vars": { "mgmt_vlan": "312", "corp_vlan": "217", "auth_srv1": "", "auth_srv2": "" }
}
```
> Assign RF/WLAN/switch templates at **org or site-group** scope; the site template seeds the
> per-site values and references, not a competing config.

## Validation
- Audits clean: site template exists with timezone + country + auto-upgrade + default RF/WLAN
  refs; sites grouped into site groups reflecting topology.
