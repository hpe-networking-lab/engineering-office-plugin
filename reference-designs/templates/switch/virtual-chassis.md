# Switch Stacking — Virtual Chassis (VC)

"Stacking" on Juniper/Mist = **Virtual Chassis**: multiple EX switches managed as one logical
device. Verified against the Juniper Mist Wired Assurance guide.

## The split (what's template vs per-device)
- **VC topology is per-stack, preprovisioned** — member **serial numbers, member IDs, and
  roles** are set in the Mist portal per physical stack. NOT in an org template, and NOT via
  site variables (it's physical hardware identity).
- **Config on the VC is template-driven** — the org/site **network template** pushes VLANs,
  port profiles, RADIUS, and features to the VC exactly like a standalone switch. Port
  profiles reference member ports by FPC: `ge-0/0/x` = FPC0, `ge-1/0/x` = FPC1, etc.

## Mist supports **preprovisioned VC only**
Each member is pinned by **serial + member ID + role** (`routing-engine`/primary, backup, or
linecard). This is intentional — it blocks accidental RE-role changes or stray members
joining the stack.

## Two formation workflows (by model)
| Switch models | How the VC is formed |
|---------------|----------------------|
| **EX2300, EX4650, QFX5120** (no dedicated VC ports) | **Form Virtual Chassis** in the Mist portal — Mist forms it. |
| **EX3400, EX4100, EX4300, EX4400** (dedicated VCPs) | Cable the dedicated VCPs + power on to form **physically first**, then **Modify Virtual Chassis** in the portal to preprovision. |

(EX4400-24X and mixed setups have model-specific procedures — see the guide.)

## Conventions to keep template config landing correctly
- **Consistent member/FPC numbering per site** — port profiles target `<type>-<fpc>/<pic>/<port>`,
  so if FPC ordering differs stack-to-stack, the wrong ports get the wrong profile. Document
  the member order as a site convention.
- **Roles:** one primary (RE), one backup, rest linecards. Preprovision explicitly.
- **Mixed-model VC** (different EX models in one stack) has mode/compatibility constraints —
  verify the models are supported together before forming.

## Provisioning vs config — where each lives
- **Provisioning time (per stack, portal):** form/preprovision the VC, assign serials/member
  IDs/roles, designate VCPs.
- **Template (org/site):** everything else — the VC inherits the network template like any
  managed switch.

## Sources
- Virtual Chassis Overview (Juniper Mist)
- Manage a Virtual Chassis Using Mist (preprovisioned / Modify VC)
- Configure a VC using EX2300/EX4650/QFX5120 (Form VC) and EX3400/EX4100/EX4300/EX4400
- Juniper Mist Wired Assurance Configuration Guide (2026-06-12)
