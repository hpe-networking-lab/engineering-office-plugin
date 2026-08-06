---
name: proxmox-ml110-provision
description: Provision bare-metal Proxmox VE on an HPE ProLiant Gen11 server (e.g. ML110, iLO 6) remotely
  over the Redfish API — inventory the box, handle the license gate, build an answer-file ISO, boot,
  install. Encodes the two blockers proven the hard way: iLO URL virtual-media may not boot (use a physical
  USB stick), and the disk is invisible until you create a single-disk RAID0 volume on the HPE MR
  controller. Use for bare-metal HPE Gen11 provisioning, iLO Redfish install, or Proxmox on new hardware.
  Trigger words: Proxmox, ML110, Gen11, iLO, Redfish, bare-metal install, virtual media, RAID0, MR
  controller, answer file, unattended install.
---

# proxmox-ml110-provision

> Remotely provision Proxmox VE on an HPE ProLiant Gen11 (iLO 6) over Redfish, grounded in the device's own
> outputs, carrying the two blockers this class of box hits. **A concrete worked example** — the portable
> lesson is the *method* (read the box over Redfish; expect the two blocker classes below). Adapt to your
> hardware. **Self-contained + configurable:** iLO/root creds come from your `credentials_file`; if your
> `standards_source` has a build guide, follow it. Governing: [[eo-guardrails]] — ground-before-assert
> (read the box, never guess), reflex 4 (rotate factory iLO password; creds out-of-band), reflex 8 (new
> infra = Human-Authority; short ADR if it becomes standing infra). Doc-first: HPE iLO 6 Redfish API ref +
> Proxmox Automated-Installation docs.

## When this fires

"Provision Proxmox on the ML110 / the new HPE box", "install bare-metal via iLO Redfish", "stand up the
Gen11 hypervisor".

## Guardrails carried from the standard

- **Ground on the box, don't assume.** Read license tier, storage, power/health from Redfish
  (`/redfish/v1/Systems/1`, `.../Storage/`, `.../Managers/1/LicenseService/`) before planning. Unknowns stay
  unknown — never guess them into config.
- **Secrets out-of-band.** iLO factory password is on the chassis label — **rotate on first login** and
  store the new value in your gitignored `credentials_file`. Default creds on a management port are the
  single biggest risk. Verify presence, never value.
- **New infra is a Human-Authority decision.** Disk layout, licensing trial, cluster join = HA's call; a
  short ADR if Proxmox becomes standing infra.

## Procedure (grounded in the verified build)

1. **Reach + identify the iLO** (find its DHCP lease / scan `:443`), confirm creds, read identity:
   ```
   curl -sk -u Administrator:'<ILO_PW>' https://<ILO_IP>/redfish/v1/Systems/1 \
     | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["Model"],d["SerialNumber"],d.get("BiosVersion"))'
   ```

2. **License gate.** Remote Virtual Media + remote console need **iLO Advanced**; Standard restricts them.
   Read the tier — don't assume. If Standard, apply the iLO Advanced trial (key from HPE's licensing portal
   — **your HPE account, out-of-band**) via `POST /redfish/v1/Managers/1/LicenseService`
   `{"LicenseKey":"..."}`, confirm it flips to Advanced.

3. **Build the answer-file ISO** (Path A, preferred): write `answer.toml` (`[global]/[network]/[disk-setup]`;
   root password from your `credentials_file`, not inline), then `proxmox-auto-install-assistant
   validate-answer` + `prepare-iso`. Host the ISO on an HTTPS URL the iLO can reach.

4. **⚠ Blocker 1 — iLO URL virtual-media may NOT boot this box.** On the reference ML110, every URL-mount
   path fell through to UEFI network boot (normal order, F11 CD *and* USB, "Run a UEFI application",
   `BootOnNextServerReset`) even though the ISO was UEFI-bootable. **Fix: a physical USB stick** (image it
   with balenaEtcher "Flash from URL" → your HTTP server). "Generic USB Boot" is first in this box's boot
   order, so a real USB block device boots immediately. **Don't burn time on virtual-media boot — go
   straight to USB.**

5. **⚠ Blocker 2 — the disk is invisible to the installer** ("could not find any supported hard disks"). The
   drive sits behind the **HPE MR RAID controller** with **zero logical volumes** (raw disk
   `StandbyOffline`); in RAID mode the OS only sees volumes. **Fix (via Redfish):** create a single-disk
   RAID0 volume —
   ```
   POST /redfish/v1/Systems/1/Storage/<MR-id>/Volumes
   {"RAIDType":"RAID0","DisplayName":"pve-boot","Links":{"Drives":[{"@odata.id":".../Drives/0"}]}}
   ```
   **Gotcha:** drives go under **`Links.Drives`**, not top-level; the POST may time out but the volume still
   creates — re-GET `/Volumes` to confirm. It then appears as `/dev/sda` and the answer file's
   `disk-list=["sda"]` matches.

6. **Boot once + install.** Boot the USB; the answer-file install runs unattended. Monitor via
   `GET /redfish/v1/Systems/1` (`PowerState`, `BootProgress`).

7. **Post-install:** reach the UI at `https://<PVE_MGMT_IP>:8006`; set the no-subscription repo if unlicensed
   + update; baseline storage/network; **rotate the iLO factory password** and store it in your
   `credentials_file`.

8. **Governance / inventory:** add the host to your inventory and run [[inventory-reconcile]] (live = truth);
   record final IPs/hostname + chosen path; short ADR if it's now standing infra.

## Verify (do not skip)

- Redfish reads (license tier, storage volume, power) confirm the intended state before each step.
- The RAID0 volume exists (`GET /Volumes`) and the installer sees `/dev/sda`.
- Proxmox UI reachable + API auth works with the stored root credential.
- iLO factory password rotated; host added to inventory + reconciled.

## Do NOT

- Do not assume the license tier or disk layout — read them over Redfish first.
- Do not sink time into iLO URL virtual-media boot on this hardware — use a physical USB stick.
- Do not leave the iLO on its factory-default password; rotate and store out-of-band.
