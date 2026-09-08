---
name: converge-or-escalate
description: Run the Fix/Repeat loop with an exit condition. Use when a fix did not work and you are about to try another one; when you are on your third attempt at the same fault; when hypotheses are being eliminated one at a time; when a bench or lab reproduction is being used to chase a customer symptom; or when you are about to change something to see what happens. Triggers - it still fails, try another approach, next hypothesis, let me try, that did not work either, still not working, ruled that out too, one more thing to check, iterate, bisect, narrow it down, we have been at this a while.
---

# converge-or-escalate — the Fix/Repeat loop, with an exit

> **Why this exists.** Discover, Build and Validate are heavily gated in this office. **Fix/Repeat is
> not**, and it is where the expensive failures live. 2026-09-05, Canyon ISD: **nine hypotheses**
> eliminated one at a time, a full engagement day, against a bench that never exhibited the fault.
> No gate fired, because no gate counts attempts. The cause was found in under an hour once David
> said "reproduce first, then bisect".
>
> A loop without an exit condition is not a method. It is a way of being busy.

## THE LOOP HAS TWO EXITS. Draw them both before you start.

```
        ┌──────────────────────────────────────┐
        │  attempt N                           │
        │   1. ONE change                      │
        │   2. predict the result FIRST        │
        │   3. run it                          │
        │   4. record it — even when it fails  │
        └──────────────┬───────────────────────┘
                       │
              did this attempt produce
              NEW INFORMATION?  ──── no ──┐
                       │ yes              │
                       ▼                  ▼
              converged? ── yes ──►  DoD   BUDGET (below)
                       │ no                    │
                       └────────────┐          ▼
                                    └──►  ESCALATE
```

**Exit 1 — CONVERGED.** You can state the mechanism and show the evidence. Go to Definition of Done.
**Exit 2 — BUDGET EXHAUSTED.** Stop and escalate. This exit is the point of the skill; a loop with
only the first exit runs until someone gets tired.

## STEP 0 — BEFORE THE FIRST ATTEMPT, spend two minutes on these

1. **CAN YOU REPRODUCE IT?** If your test rig has never shown the fault, **you cannot bisect on it.**
   Subtraction finds only single-variable causes; if the cause is conjunctive, every input clears
   individually and you find nothing. Establishing reproduction IS the work — do not treat it as a
   prerequisite you skip because it is slow. *(gate: `reproduce-before-you-bisect`)*
2. **NAME THE OBSERVATION — not the concept.** What would you have to WATCH HAPPEN to believe it is
   fixed? Not "filtering works" but "a client behind the firewall requests a known-blocked URL and
   gets the block page." Then show that observation has been made before ON THIS PLATFORM; if no
   known-good instance exists, the failure is unverified and establishing what healthy looks like IS
   the first task. **If you cannot name the observation, stop — that is a discovery finding, not a
   loop to enter.** Say so and ask. Iterating toward an undefined target is how a loop runs forever.
   *(gate: `validate-the-success-criterion-before-chasing-it`)*
3. **RUN THE DIAGNOSTIC ORDER FIRST.** `lab_search` the symptom → reachability → baseline diff →
   falsify from the record. Most loops that run long never ran step 0.
4. **WRITE THE BUDGET DOWN.** Say, out loud and in the record, how many attempts you will make before
   escalating, and what you would escalate WITH. A budget you did not write is not a budget.

## THE BUDGET

**Default: THREE attempts that produce no new information.** Not three attempts — three *uninformative*
ones. An attempt that fails but narrows the space is progress and does not count against you.

**The test after every attempt: what do I know now that I did not know before?** If the honest answer
is "that this one also did not work", that is one against the budget. Three of those and you stop.

Stop EARLIER than the budget, immediately, if any of these fire:

- **The same fix has been applied twice.** Re-applying a change that did not take is not a second
  attempt; it is the first attempt repeated because you did not find out why it did not take.
- **You are changing something to see what happens.** That is experimentation, not implementation.
  Load the procedure. *(gate: `stay-on-rails-implement-dont-experiment`)*
- **More than one novel vendor defect** has appeared in the session. That is a claim about your own
  recent changes, not about the vendor. *(gate: `count-your-defect-claims`)*
- **You are about to change a second thing** because the first change did not help. One change per
  attempt or you cannot attribute the result.
- **A result contradicts a control that just passed.** Suspect the instrument before the system.
- **You have contaminated the rig.** See the next section — this one ends the loop outright.

## THE RIG IS AN INSTRUMENT. DO NOT CONTAMINATE IT.

Before any attempt that changes SHARED state — a bench tenant, a default object, a template others
inherit — **ask what later reads depend on it.** An attempt that alters the thing subsequent attempts
will measure destroys those attempts, and the damage is invisible: results still arrive, they are just
no longer evidence.

2026-09-05, Canyon: an OCR-overwrite rehearsal altered the default objects later tests were reading.
**Three subsequent results had to be downgraded from `[proven]` to `[observed]`, and one was
unreadable entirely.** The session's own words: *"Three tests are now compromised by one action of
mine."* Instrument repair became the blocker.

**If you contaminate the rig, the loop is over until the rig is restored.** Say so, restore it, and
diff to prove restoration. Do not keep iterating on a compromised instrument and hope.

## RECORD EVERY ATTEMPT, ESPECIALLY THE FAILURES

**This is the half that gets skipped, and it is the expensive half.** A rejected approach that is not
written down is re-derived at full cost by the next session — and the next session is often you, on
Monday, with the context compacted away.

Per attempt, one line in the effort's `DECISIONS.md`:

```
attempt N — CHANGED: <the one thing> — PREDICTED: <what you expected> —
            OBSERVED: <what happened> — LEARNED: <what the space lost> — [proven|observed|inferred]
```

**Write it when the attempt ends, not at the end of the loop.** An intention is not a record, and a
loop summary written afterwards is a reconstruction.

Worked examples of this paying off: `D-16` in poc-builder-tool — *a browser cannot be made to open a
file dialog in a chosen folder*, several turns to establish, recorded so nobody re-derives it. And
Canyon's rejected paths, which is why its successor did not re-run them.

## WHEN THE BUDGET IS EXHAUSTED — HOW TO ESCALATE

**Escalation is not "I am stuck".** It is a handoff with a receipt. Hand over:

1. **The success criterion** and whether it has ever been met here.
2. **The attempt table** — every attempt, what changed, what was predicted, what was observed.
3. **What the space has LOST** — hypotheses genuinely eliminated, with the evidence that killed them.
   This is the value you built; without it the next person starts at attempt one.
4. **What you could NOT test, and why** — missing instrument, contaminated rig, customer-side access,
   an approval you do not hold.
5. **Your best remaining hypothesis, labelled as one**, and the single cheapest read that would
   settle it.

Escalate to a human when it needs authority, spend, customer contact or a decision only they hold.
Escalate to the coordinator when it needs an instrument, a tenant, or hardware you cannot reach.
**Escalating is a result, not a failure** — a bounded loop that reports honestly is worth more than
an unbounded one that eventually stumbles into an answer nobody can reproduce.

## DEFINITION OF DONE — the other exit

Do not take this exit on "it works now". Take it when:

- The **success criterion** stated at step 0 is met, verified on the **authoritative source** — the
  device's own CLI or config, never a proxy signal, never the API echo.
- You can **state the mechanism**. "It started working" is not convergence; it is a coincidence you
  have not investigated. If the fix worked and you cannot say why, say that plainly.
- The change is **recorded with what it rests on** — `[proven]` / `[doc-grounded]` / `[inferred]`.
- **Anything you broke or contaminated on the way is restored**, and you diffed to prove it.
- **David closes.** Never declare a thing done. State the end-state and what remains.

## THE ONE-LINE VERSION

**Reproduce before you bisect. One change per attempt. Three uninformative attempts and you stop.
Record the failures. Escalate with the map, not the frustration.**
