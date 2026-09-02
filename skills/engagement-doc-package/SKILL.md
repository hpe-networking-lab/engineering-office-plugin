---
name: engagement-doc-package
description: Produce the required engagement deliverable set to the documentation standard — Discovery →
  ADR → Architecture Recommendation (exec-summary first) → DESIGN → topology drawing → baseline capture →
  deployment/validation review, with traceability. Use whenever a customer engagement needs its
  documentation package created or checked for completeness, or someone asks for the deliverables / write-
  up / hand-off docs for a design. Trigger words: engagement docs, deliverable set, ADR, architecture
  recommendation, executive summary, DESIGN doc, HLD, LLD, validation review, hand-off package.
---

# engagement-doc-package

> Produce (or completeness-check) the deliverable set every engagement hands a customer — to the standard,
> with traceability, validated to ground truth. **Self-contained + configurable:** if your
> `standards_source` defines a documentation standard, follow it as authoritative; otherwise the set below
> is your standard. Maps onto the phase folders from [[engagement-scaffold]]. Governing:
> [[eo-guardrails]] — validate-to-the-wire, ground-before-assert, secrets discipline, sanitize before
> sharing.

## When this fires

"Write up the engagement", "produce the deliverables for <design>", "do we have the full doc package?",
"draft the architecture recommendation / ADR / DESIGN", "prep the customer hand-off docs".

## The required artifacts (all seven — this is the bar)

| # | Artifact | Phase | Purpose / audience |
|---|---|---|---|
| 1 | **Discovery notes** | `01_Discovery` | What the customer has and needs; requirements, constraints, "what we need from them". |
| 2 | **ADR(s)** — decision records | `02_Engineering` | Each material decision: context, options, trade-offs, decision, **validation**, revisit triggers. |
| 3 | **Architecture Recommendation** (with **Executive Summary**) | `03_HLD` | Recommended design and *why*, opening with a leadership-readable exec summary; options set aside. |
| 4 | **DESIGN** — low-level design | `04_LLD` | Components, flows, exact config, ports, constraints. Implementable. |
| 5 | **Topology / flow drawing** | `03/04` | A real diagram file (SVG/drawio), **not ASCII**, and **RENDERED and looked at** before it ships (see the render gate below). Auth/traffic/trust flow as needed. |
| 5b | **Assumptions register** | `03_HLD` | Every unknown we determined or recommended rather than asked about: *"we have assumed X; if X is wrong, Y changes."* See the classify-the-unknown gate below. |
| 6 | **Baseline capture** | `05/06` | Live pre-change state so change is diffable + reversible — use [[config-backup]]. |
| 7 | **Deployment / validation review** | `07/08` | What was deployed and **how the design was validated** to the observable effect (wire/packet/behavior). |

## Guardrails carried from the standard

- **Validate to ground truth.** Every testable design claim needs evidence (a packet, a behavior, a
  schema-valid render) recorded in the ADR's *Validation* section and/or the deployment review — reflected
  in config, not just documented. Doc-conformance is not validation.
- **Exec summary is mandatory** in the Architecture Recommendation (audience includes non-engineers).
- **Drawings are real files** (SVG/drawio), version-controlled next to the design — never ASCII art —
  and **RENDER EVERY DRAWING AND READ THE IMAGE BACK BEFORE SHIPPING IT.** Well-formed is not correct:
  a drawing you have not rendered is a claim, not an artefact. Render twice — browser scale, and the
  width it will be printed at (A4 landscape @150dpi = `output_width=1754`):
  ```
  /lab/venvs/svg/bin/python -c "import cairosvg; cairosvg.svg2png(url='x.svg', write_to='x.png', output_width=1754)"
  ```
  *(2026-09-02, McKinney HLD: a well-formed SVG that looked right in source had a label overflowing
  into two adjacent boxes, an annotation crossed by four diagonal links, and two note lines in the
  wrong order. All three would have shipped.)*
- **CLASSIFY EVERY UNKNOWN BEFORE IT BECOMES A CUSTOMER QUESTION.** Three kinds, and only one of them
  is a customer question:
  | kind | where it belongs | test |
  |---|---|---|
  | we can determine it | our own work — the config, the export, the API | could any instrument we have, or have asked for, answer this? |
  | we should recommend it | the design, as a recommendation | is this a choice the customer is paying us to make? |
  | only they know it | the customer ask | intent, plans, constraints, what breaks, what is leaving |
  The first two become the **assumptions register** in the Architecture Recommendation, never
  questions. A question asks the customer to do our analysis; an assumption invites them to correct
  it. *(2026-09-02, McKinney ISD: a 19-question information request was rejected by the Human — one
  question stated our own conclusion and asked them to confirm it.)*
- **A stencil label is not an instrument reading.** Model strings lifted from a customer drawing
  (`N9K-...`, `Model 9800-80`) are `[record]` about the SHAPE someone picked from a palette. Nothing
  may be sized, counted or priced from them, and they do not close a "no device models" blocker.
  Adjacency claims come from the RENDERED page, never from extracted text.
- **Traceability:** the Recommendation cites the ADR(s); the DESIGN cites the Recommendation; the
  validation review cites the acceptance criteria. Keep the chain intact.
- **Secrets never in the package** — reference your `credentials_file`; **scrub before any external share**
  ([[sanitization-gate]] + Human-Authority approval).

## Procedure

1. **Locate/scaffold** the engagement phase folders ([[engagement-scaffold]]); confirm the state file is
   valid.
2. **Discovery (01):** requirements, constraints, what's needed from the customer.
3. **ADR(s) (02):** one per material decision — context, options, trade-offs, decision, **Validation**
   (evidence), revisit triggers.
4. **Architecture Recommendation (03):** exec summary first, then the design and why; cite the ADR(s).
5. **DESIGN (04):** components, flows, exact config, ports, constraints; cite the Recommendation.
6. **Topology drawing (03/04):** a real SVG/drawio of the flow.
7. **Baseline capture (05/06):** [[config-backup]] the live pre-change state.
8. **Deployment / validation review (07/08):** what was deployed and how it was validated to the observed
   effect; cite the acceptance criteria.

## Minimum bar (compact designs)

A compact design may collapse to four files: `Architecture-Recommendation.md` (with exec summary),
`DESIGN.md`, one `ADR` (with validation evidence), and one topology `.svg` — plus a pointer to the
validation log. **That is the floor; do not ship fewer.**

## Verify (do not skip)

- All seven artifacts present (or the four-file floor), in the right phases.
- **Every drawing rendered, and the image actually viewed** — at browser scale AND at print width.
- **The assumptions register exists** and no question in the customer ask is one we could answer.
- Traceability resolves (Recommendation → ADR; DESIGN → Recommendation; review → acceptance).
- Each ADR has a real Validation section with evidence.
- Sanitization + Human-Authority approval done before any external share.
