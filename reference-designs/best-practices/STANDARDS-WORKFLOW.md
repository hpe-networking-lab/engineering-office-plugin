# Standards Workflow — how a lesson becomes a standard without drift (binding)

When any chat hits a generalizable problem and fixes it, follow this so the fix reaches every chat
**without going out of sync**. Rule of thumb: **one home, one writer, inherit — never copy.**

## Lanes (this is what prevents drift)
- **`best-practices/`** = the single canonical home. The **daily `lab-drift-check` is the single writer**
  here — it promotes proposals into `best-practices/` **only on David's explicit approval**. No other
  chat writes `best-practices/`.
- **`proposals/`** = the intake inbox. **Any chat may drop a proposal file here** (append-only; never
  edit someone else's). No customer/build chat edits `best-practices/` directly.

## Workflow
1. **Fix + capture (discovering chat).** Fix your own issue. Write the generalizable lesson using
   `proposals/PROPOSAL_TEMPLATE.md` (fill `Discovered by:` with your engagement/repo) and **commit it to
   `proposals/`** (git from `...`). Do NOT touch `best-practices/`. Any engagement-local
   applied copy is clearly marked as a mirror.
2. **Surface + decide (daily drift-check).** The daily `lab-drift-check` morning report **lists** every
   open proposal — title, who raised it, target file, and the one-line rule — and asks you to
   **approve or reject in that report**. That is the whole review surface; there is no separate relay and
   you never paste standard *content* between chats.
3. **Promote (drift-check = single writer, on your approval).** When you approve in the report, that
   session shows the diff, applies the rule to its `Target` file under `best-practices/` (new file or
   edit), commits/pushes, records the decision in `proposals/decided/`, **deletes the proposal** so it
   can't go stale, and appends a one-line "lesson adopted" note back in the originating engagement repo.
   Rejected → your reason is recorded and the proposal is moved to `proposals/decided/`; `best-practices/`
   is untouched.
4. **Inherit (automatic).** Because every grounding reads *all of* `best-practices/` ("binding as it
   grows") at self-ground, the new standard reaches every chat on its next session with **no re-paste
   and no per-chat sync.** That is the whole point.

## Anti-desync guardrails
- **One writer to `best-practices/`** — the drift-check, on approval. Discovering chats propose; they do
  not write the standard. (This replaces the old "relay to the mist-reference-designs chat" step; the
  approve-and-promote now happens in the drift-check report you already read each morning.)
- **Promoter closes the loop** — record the decision in `proposals/decided/` and delete the promoted/
  rejected proposal. Open proposals are the only backlog and should be short-lived.
- **Applied copies are read-only mirrors** ("snapshot of best-practices/ as of <date>"), never authority.
- **Grounding hooks** are per-repo (added once, in that repo's own chat); the grounding template
  (your effort's grounding template) carries the hook so new chats inherit by
  construction.

## Automation
The daily `lab-drift-check` **lists** open `proposals/` each morning (title / source / target / rule)
and promotes the ones you approve — right there in the report — recording the decision and notifying the
origin repo. Human Authority (David) is the gate: nothing is promoted or rejected without an explicit
in-report decision.
