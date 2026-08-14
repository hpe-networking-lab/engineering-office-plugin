#!/usr/bin/env python3
"""Structural validator for the Engineering Office plugin. Stdlib-only, no network.
Checks: manifests parse + versions agree; every SKILL.md has name/description frontmatter and the
name matches its directory; [[skill]] cross-references resolve; key referenced files exist.
Run: python3 scripts/validate.py   (exit 0 = pass)."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors, warnings = [], []
def err(m): errors.append(m)
def warn(m): warnings.append(m)

# --- manifests ---
try:
    pj = json.load(open(os.path.join(ROOT, ".claude-plugin/plugin.json")))
    mp = json.load(open(os.path.join(ROOT, ".claude-plugin/marketplace.json")))
    for k in ("name", "version", "description"):
        if not pj.get(k): err(f"plugin.json missing '{k}'")
    pv = pj.get("version")
    if mp.get("version") != pv: err(f"marketplace.json version {mp.get('version')} != plugin.json {pv}")
    plugins = mp.get("plugins", [])
    if not plugins: err("marketplace.json has no plugins[]")
    for p in plugins:
        if p.get("name") == pj.get("name") and p.get("version") != pv:
            err(f"marketplace plugins[{p.get('name')}].version {p.get('version')} != {pv}")
    print(f"manifests: name={pj.get('name')} version={pv}")
except Exception as e:
    err(f"manifest parse failed: {e!r}")

# --- skills ---
skills_dir = os.path.join(ROOT, "skills")
skill_names = set()
if os.path.isdir(skills_dir):
    for d in sorted(os.listdir(skills_dir)):
        sp = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(sp):
            err(f"skill '{d}' has no SKILL.md"); continue
        t = open(sp, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", t, re.S)
        if not m: err(f"{d}/SKILL.md: missing YAML frontmatter"); continue
        fm = m.group(1)
        name = re.search(r"^name:\s*(.+)$", fm, re.M)
        desc = re.search(r"^description:\s*\S", fm, re.M)
        if not name: err(f"{d}/SKILL.md: no 'name:' in frontmatter")
        elif name.group(1).strip() != d: err(f"{d}/SKILL.md: name '{name.group(1).strip()}' != dir '{d}'")
        if not desc: err(f"{d}/SKILL.md: no 'description:' in frontmatter")
        skill_names.add(d)
    print(f"skills: {len(skill_names)} found")

# --- [[cross-references]] across all markdown ---
for dp, _, files in os.walk(ROOT):
    if "/.git" in dp: continue
    for f in files:
        if not f.endswith(".md"): continue
        for ref in re.findall(r"\[\[([a-z0-9-]+)\]\]", open(os.path.join(dp, f), encoding="utf-8").read()):
            if ref not in skill_names:
                warn(f"{os.path.relpath(os.path.join(dp,f),ROOT)}: [[{ref}]] not a known skill")

# --- key referenced files exist ---
for rel in ("grounding/PROJECT-INSTRUCTIONS.md", "grounding/CHAT-SEGMENTATION.md",
            "skills/eo-guardrails/SKILL.md", "reference-designs/templates/effort-registry.md",
            "README.md", "SETUP.md", "config/eo.config.example.yaml"):
    if not os.path.isfile(os.path.join(ROOT, rel)): err(f"missing referenced file: {rel}")

# --- report ---
for w in warnings: print("WARN:", w)
for e in errors:   print("FAIL:", e)
print(f"\n{'PASS' if not errors else 'FAIL'} — {len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
