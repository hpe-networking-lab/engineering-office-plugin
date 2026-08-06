# RF Templates — Baseline, High-Density, Outdoor

**Principle:** let **Mist AI RRM** manage channel and power. Pin nothing without a documented
reason. Keep a **small set** of RF templates (not one per site) and split **indoor vs outdoor**.

## Per-band recommendations
| Band | Width | Power | Notes |
|------|-------|-------|-------|
| 2.4 GHz | **20 MHz only** | AI-managed (or 12–17 dBm) | Channels **1/6/11** only. Disable in dense areas if 5/6 GHz covers. |
| 5 GHz | 40 or 80 MHz | AI-managed (17–23 dBm) | Let AI pick from non-DFS or DFS+non-DFS. |
| 6 GHz | 80 MHz (160 for high throughput) | AI-managed | Use **PSC** channels. |

## Baseline (indoor) — Mist API skeleton
`POST /api/v1/orgs/{org_id}/rftemplates`
```json
{
  "name": "Indoor-Baseline",
  "band_24": { "disabled": false, "channels": [1,6,11], "bandwidth": 20, "power_min": 8, "power_max": 17, "allow_rrm_disable": false },
  "band_5":  { "disabled": false, "bandwidth": 80, "power_min": 8, "power_max": 20, "channels": [] },
  "band_6":  { "disabled": false, "bandwidth": 80, "power_min": 8, "power_max": 18, "channels": [], "standard_power_enabled": false }
}
```
Empty `channels` on 5/6 GHz = let AI RRM select. `power_min/max` gives RRM a range rather
than a fixed value.

## High-density (venues, gate areas, large halls)
- Narrower cells: 5 GHz **40 MHz**, tighter power range, 2.4 GHz often **disabled** to cut
  co-channel. Enable band steering to push clients to 5/6 GHz. Justify the override (density).

## Outdoor / ramp
- Separate template. Wider power range allowed for distance; channel exclusions per
  regulatory/terrain; 6 GHz typically indoor-only. Document the outdoor justification.

## Validation
- Audits clean: 2.4 GHz 20 MHz + 1/6/11, no fixed channels/power without justification, ≤ a
  few templates, indoor/outdoor split.
