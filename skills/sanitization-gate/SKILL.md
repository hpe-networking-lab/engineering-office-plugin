---
name: sanitization-gate
description: Zero-tolerance scan for customer identifiers and secrets BEFORE anything is shared publicly or
  externally — a repo going public, a sanitized sample, a shared skill, an exported doc. Use whenever
  content is about to leave your private/internal boundary, or someone asks to publish, open-source, share
  externally, or sanitize an artifact. The gate that pairs with Human-Authority approval for public
  release. Trigger words: sanitize, scrub, review before public, publish, open-source, make public,
  redact, customer identifiers, leak check, before we share.
---

# sanitization-gate

> The zero-tolerance check that protects customer identifiers and secrets before any public or shared
> release. **Nothing crosses the private/internal boundary without this scan AND explicit Human-Authority
> approval.** **Self-contained** — no external resource required. If your `standards_source` defines a
> sanitization standard, follow it as authoritative; otherwise this is your standard. Governing:
> [[eo-guardrails]] — reflex 8 (making anything public is a gated action), reflex 4 (secrets). Pairs with
> [[engagement-doc-package]] (scrub before external hand-off).

## When this fires

"We're about to make <repo> public", "publish the sanitized sample", "share this externally",
"open-source it", "scrub this before we send it", "is this safe to share?"

## Hard rule

Publishing to a public repo/marketplace, flipping a repo to public, or sharing an artifact outside your
private boundary is a **gated action** — surface it and get explicit Human-Authority approval **before** it
goes out, even when scans are clean. **Verify a repo is private before you push** anything not cleared for
public (an anonymous `GET api.github.com/repos/<org>/<repo>` returning **404** means private; **200** means
public — check, don't assume). Standing rule: private work is autonomous; **anything public comes back to
Human Authority.**

## What to scan for (zero tolerance — any hit blocks the release)

- **Customer identifiers:** customer/site names, real people's names + emails, physical addresses,
  customer domains, engagement/project code-names, ticket numbers.
- **Environment fingerprints:** real public IPs/subnets, real MACs, org/site **IDs**, serial numbers,
  claim/activation codes, customer SSIDs, hostnames.
- **Secrets:** RADIUS/ISE shared secrets, PSKs, API tokens, OSPF/SNMPv3 keys, private keys/certs,
  passwords — even "example" ones. Verify **presence, never value**.
- **Residual references:** paths, comments, commit messages, screenshots, drawing metadata, file names.
  **Check git history, not just the working tree.**

## Procedure

1. **Define the release boundary** — exactly which files/repo/branch is going out, and the destination. If
   public, flag that Human-Authority approval is required before the final step.
2. **Scan the working tree** for identifier + secret patterns, and for the known customer/site names for
   your context (keep that list out-of-band). Treat every hit as blocking until cleared or confirmed
   generic.
3. **Scan git history** — a public repo exposes all of it. If history carries secrets/identifiers,
   working-tree cleanup is **not** enough: rewrite history (destructive → Human-Authority approval) or
   re-home the content into a fresh repo.
4. **Replace, don't just delete** — swap real values for clearly-fake placeholders (`example.com`,
   RFC-5737 doc IPs `192.0.2.0/24`, `AA:BB:CC:00:00:01`, `{{RADIUS_SECRET}}`) so the artifact still
   teaches. Secrets live only in your gitignored `credentials_file`, never inline.
5. **Second pass / diff** — re-run the scans; the bar is **zero residual identifiers**.
6. **Record the evidence** and **hand to Human Authority for the public-release approval.** Only on
   explicit yes does it go out.

## Reference scan (starting point — grow it for your context)

```
grep -rInE '([0-9]{1,3}\.){3}[0-9]{1,3}|([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}|BEGIN [A-Z ]*PRIVATE KEY|-----BEGIN|password|secret|token|psk|claim' <path>
git log -p | grep -inE '<same patterns + your known customer/site names>'
```

## Do NOT

- Do not publish or flip-to-public without explicit Human-Authority approval — even if scans are clean.
- Do not rely on working-tree cleanup when git history still carries identifiers.
- Do not print secret values while scanning — match on presence/pattern; report location, not value.
- Do not fold customer or active-engagement data into any shared/public artifact — sanitize first.
