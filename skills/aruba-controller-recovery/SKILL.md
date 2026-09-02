---
name: aruba-controller-recovery
description: >-
  Recover an Aruba 70xx/72xx/90xx controller you cannot log into, or that arrived second-hand
  still bound to someone else's Mobility Conductor. Use when the admin password is unknown, when
  configure terminal is refused with "This controller is managed by a Mobility Conductor" or
  "Mobility Master", when a controller boots but is unreachable on an address it reports as up,
  or when a bootloader factory-reset has left it unable to finish starting. Trigger words —
  cannot log into controller, forgot controller password, password recovery, forgetme, managed by
  a Mobility Conductor, managed by a Mobility Master, used controller, second-hand Aruba, write
  erase all permission denied, format 0:2, cpboot, apboot, ancillary files are not present,
  additional image upgrade is required, controller up but not pingable, VLAN 4094, AOS 8 enable
  mode, bootdelay.
---

# Recovering an Aruba controller from unknown or second-hand state

**Status: `[proven]` — every step below was executed end to end on a 7005 (S/N CP0026514) on
2026-09-01, including the mistakes. Roughly four hours, most of it avoidable with this file.**

## 0. Before you touch anything

**Get a console. Everything here needs one.** 9600 8N1. The recovery account works on the
serial console ONLY, never over SSH, by design.

**Establish which OS generation it runs before choosing a procedure.** AOS 6, AOS 8 and AOS 10
differ, and guidance written for one will strand you in another. The boot banner names it.
Getting this wrong is the single biggest time sink here (see section 6).

**If the box is second-hand, assume the previous owner still holds the GreenLake claim.** That
is separate from anything on the box, and no amount of console work releases it (section 7).

## 1. The deadlock, and why the vendor doc does not warn you

The documented recovery is: log in on console as `password` / `forgetme!`, then
`configure terminal` then `mgmt-user admin root`. That account is enabled by default.

On a conductor-bound controller this deadlocks:

| you try (as the recovery user) | you get |
|---|---|
| `configure terminal` | `This controller is managed by a Mobility Conductor.` |
| `write erase all` | `You do not have permission to execute this command` |
| `show version` | `You do not have permission to execute this command` |
| `disaster-recovery on` | permission denied |

The recovery user's ONLY privilege is resetting the admin password. That needs config mode.
Config mode is what the conductor binding blocks. Every door needs a key held behind another
door.

## 2. What actually breaks the deadlock, in order

### 2a. `cd /mm` first  `[proven]`

AOS 8 has a node hierarchy. Config mode is refused at the default node but **opens at `/mm`**:

```
cd /mm
configure terminal
mgmt-user admin root
```

**This is what worked.** Try it before anything destructive. If it opens: set the password,
`exit`, `write memory`, log back in as `admin`, and you have a normal controller.

### 2b. `write erase all` as ADMIN, not as the recovery user

Once you are admin this clears the config **and the deployment role**, and boots into the
Initial Setup dialog. It also drops the licence database, which is fine on second-hand kit
because those licences were never yours.

### 2c. Bootloader `format 0:2` is the LAST resort and it has a cost  `[proven]`

Interrupt boot with **`Ctrl+X`** (not Enter), then at `cpboot>`: `format 0:2`, wait, `reset`.

This breaks the conductor binding when nothing else will, **and it destroys the ancillary
filesystem**. Afterwards the box boots partway and stops. See section 3.

## 3. "Ancillary files are not present" means write the image TWICE  `[proven]`

After `format 0:2`, boot halts with:

```
Installing ancillary FS   [ FAIL : Ancillary files are not present ]
...
WARNING: An additional image upgrade is required to complete the installation of the
         AP and WebUI files. Please upgrade the boot partition again and reload.
```

**Read it literally.** The first image write installs the OS; a second write installs the
AP/WebUI ancillary files. One write leaves a box that will not finish starting.

This is not version-specific: a fresh AOS 8.10.0.21 failed at exactly the point the AOS 10.2
beta did. The missing files live on shared flash rather than inside either image, which is why
the failure follows you across partitions.

## 4. Check BOTH partitions before assuming the worst  `[proven]`

At `cpboot>`, `osinfo` reads and verifies both banks. On the 7005 it showed:

```
Partition 0:0   ArubaOS 10.2.0.0-beta   (broken by the format)
Partition 0:1   ArubaOS 6.5.1.4         image verify PASS   <- this is what saved it
```

**A second bootable image is a working CLI, and a working CLI turns a bootloader rescue into a
routine `copy tftp:`.** Use `def_part 1` then `reset` to try it. AOS 6 tolerated the missing
ancillary files and started; AOS 8 and AOS 10 did not.

Note `osinfo` reads the whole image and then hands control back to autoboot, so expect to catch
the prompt again afterwards.

## 5. Bootloader quirks that waste time  `[proven]`

- **The interrupt key is `Ctrl+X`.** The banner says so. Enter does nothing.
- **`bootdelay` is `0`** out of the box, so you are racing a zero-second countdown. Fix it
  first: `setenv bootdelay 10` then `saveenv`. `purgeenv` restores defaults.
- **`netretry=no`** by default, so a network transfer gives up on the first hiccup.
  `setenv netretry yes` before any TFTP work.
- **`reload` does not exist at `cpboot>`. The command is `reset`.**
- **`wipe out flash` is not the smaller hammer.** It erases the OS image as well and leaves you
  recovering over TFTP from the bootloader. `format 0:2` targets the config partition; prefer
  it.

## 6. AOS 6 vs AOS 8: commands that vanish between generations  `[proven]`

- **AOS 8 has NO enable mode.** `enable secret` does not exist and there is nothing to set; you
  log in already privileged. (Confirmed by an HPE employee on Airheads.) AOS 6 does need
  `enable`.
- AOS 6 offers `full-setup` / `mini-setup` at an auto-provisioning prompt. **Take
  `full-setup`** — `mini-setup` is the branch role and never offers the deployment role.
- That prompt has a short confirm window. Pre-stage `full-setup` and `yes` on the clipboard and
  paste both. Missing the confirm leaves a booted, unconfigured box that will not re-offer the
  menu until you `write erase all` again.

## 7. The GreenLake claim is NOT on the box  `[proven]`

A second-hand controller is very likely still claimed in the previous owner's GreenLake
workspace. Adding it to yours returns:

```
device already exists in workspace or invalid serial/MAC combination
```

**That string conflates two causes and cannot distinguish them.** Do not read it as a bad
serial. Confirm the serial is absent from your own workspaces, then open an HPE support case to
have it released. Nothing done on the console changes this.

## 8. It reports the interface up and you still cannot reach it  `[proven]` — cost an hour

```
show ip interface brief
  vlan 1     192.168.86.29/24    up   up
```

...and it does not answer. **Check port-to-VLAN membership before suspecting anything else:**

```
show port status     -> which port is actually Up
show vlan            -> which VLAN that port belongs to
```

On a factory-default 7005:

```
VLAN 1      GE0/0/1-0/3     <- where your address probably is
VLAN 4094   GE0/0/0         <- where your cable probably is
```

**GE0/0/0 sits in VLAN 4094, not VLAN 1.** An address on VLAN 1 reads `up/up` and is
unreachable because VLAN 1 holds no live port. Worse, the upstream switch still learns the MAC
(frames arrive untagged), so link state, speed and MAC table all look healthy and confirm the
wrong hypothesis.

**Fix: move the cable to GE0/0/1**, already in VLAN 1. No config change, no restart.

**But read section 9 first.**

## 9. GE0/0/0 may be POWERING the controller  `[proven]`

The 7005 accepts PoE and GE0/0/0 is the PoE port, so **moving that cable cuts power to the
box**. Fit the PSU before re-cabling. The tell is in the boot log:

```
Power: 802.3at POE+
Cause: POE Power Cycle
```

## 10. Order of operations that works

1. Console on, `Ctrl+X`, `setenv bootdelay 10`, `saveenv`, `osinfo` — know what you have.
2. Boot normally. Try `cd /mm` then `configure terminal` then `mgmt-user admin root` (2a).
3. If you are admin: `write erase all`, restart, `full-setup`, choose **standalone** (2b, 6).
4. Only if both fail: `format 0:2`, `reset`, expect section 3, boot the other partition (4),
   TFTP the image, **write it twice**, restart.
5. Cable into GE0/0/1 with the PSU fitted (8, 9).
6. Treat the GreenLake claim as a separate problem (7).

## 11. What NOT to do

- **Do not run `format 0:2` before confirming a recovery image is reachable.** On 2026-09-01 the
  image was already on the lab at `/lab/shared/ArubaOS_70xx_8.10.0.21_94501` and nobody checked.
  That single omission turned a locked box into a non-starting one for two hours.
- **Do not trust community guidance without checking the OS generation.** The `format 0:2`
  procedure dates from 2014 and was written for AOS 6-era 70xx/72xx. It still breaks the lock,
  but on a newer flash layout it takes the ancillary filesystem with it, and that consequence is
  documented nowhere.
- **Do not read "already exists in workspace" as a bad serial** (7).
- **Do not call a port or cable dead when the interface reports up/up** — check VLAN membership
  first (8).
