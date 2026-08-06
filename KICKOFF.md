# Onboarding kickoff — paste into a NEW Cowork chat

One paste. It walks you through installing the plugin, sets you up, and runs a read-only shakedown to prove
it works. (The two `/plugin` lines are slash commands you run yourself — Claude can't run them for you — so
step 0 hands them to you and waits.)

```
You are helping me — a new engineer joining a networking engineering practice ("the Engineering Office") —
set up my Cowork environment, then proving it works with a read-only shakedown. Drive this end to end: do
everything you can yourself; for the few things only I can do (run slash commands, change app settings, enter
credentials), give one crisp instruction and wait for me to confirm. Be self-sufficient and bounded —
everything here is READ-ONLY; never write to any tenant or touch a customer environment.

STEP 0 — Install the plugin. You can't run slash commands, so tell me to run these two in this chat, then
wait for me to confirm they succeeded before continuing:
  /plugin marketplace add https://github.com/hpe-networking-lab/engineering-office-plugin.git
  /plugin install engineering-office-plugin@engineering-office-marketplace

1. Confirm it's active: list the skills you now have and load the eo-guardrails grounding. State back, in one
   sentence, the gates you now follow.

2. Configuration: follow SETUP.md — copy config/eo.config.example.yaml to eo.config.yaml and fill it for my
   setup (ask me for my workspace folder; default to local mode). Show me the finished file.

3. Connector: use the connector-setup skill to stand up MY OWN hpe-networking MCP connector — my own Docker,
   my own platform credentials, nothing shared. Do everything you can yourself; I'll confirm Docker is
   running and enter the secret values. When it's up, verify it read-only.

4. Shakedown: run the onboarding-shakedown skill — connector health check, load and run a read-only audit
   skill against a test/lab org, a grounding test against reference-designs/, and (if I give you a sample
   config) one bounded read-only review. Report after each step.

5. Readiness + handoff: tell me what passed and what still needs an input. From there I direct my own work as
   the Human Authority. Name this chat and every future one WHO-FIRST ("<Customer>: <effort>" for customer
   work, "Lab: <effort>" for lab work).

If a step can't run yet (no credential, no sample config), say so and continue — don't fake a pass, and never
write to any tenant.
```
