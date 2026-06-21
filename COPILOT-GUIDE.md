# Using this kit with GitHub Copilot CLI (step-by-step)

How the `.md` files are discovered, where to put them, and the exact sequence to run the
MAP → BUILD → VERIFY loop in the pod. (Mechanics verified against GitHub Docs — see the
links at the bottom.)

## How GitHub Copilot CLI discovers your files

| Kind | File | Where it goes | How you use it |
|---|---|---|---|
| **Skill** | `SKILL.md` in a folder | personal: `~/.copilot/skills/<name>/` · project: `.github/skills/<name>/` | invoke with `/<name>` in your prompt |
| **Custom agent** | `<name>.agent.md` | `~/.copilot/agents/` (home wins over repo) | the colleagues' `baa-analysis` etc. live here |
| **Always-on instructions** | `copilot-instructions.md` | `~/.copilot/copilot-instructions.md` or repo `.github/copilot-instructions.md` | auto-applied to every request |

> **Critical gotcha:** a skill's `name:` frontmatter **must equal its folder name**, or
> the skill silently won't load. Ours already match (`bafa-map`, `bafa-build`,
> `bafa-verify`). After adding skills, run `/skills reload`; check with `/skills info bafa-map`.

## Step 0 — get the kit into the pod
```bash
git clone <this-repo> ~/bafa-comp-modernize        # or copy it in
```

## Step 1 — install the three skills (recommended, reusable)
```bash
cp -r ~/bafa-comp-modernize/skills/* ~/.copilot/skills/
```
Then start `copilot` and:
```
/skills reload
/skills info bafa-map        # confirm it loaded (repeat for bafa-build, bafa-verify)
```
**Zero-install alternative:** skip this and just tell copilot to read the file, e.g.
`Read ~/bafa-comp-modernize/skills/bafa-map/SKILL.md and follow it for the Compensation widget.`
copilot reads files in its working directory — this always works.

## Step 2 — VERIFY the dashboard now (this is the ticket; no build needed)
```bash
cd ~/bafa-comp-modernize/verify
pip install -r requirements.txt && python -m playwright install chromium
cp config.example.json config.json
( cd …/BAX-BusinessAnalysis/business-analysis-next-ui && npm install && npm run dev )   # :5173
```
In `copilot`:
```
Use the /bafa-verify skill to run --screen dashboard and summarize output/report-dashboard.html
```
…or just run it yourself: `python parity/run_parity.py --screen dashboard`.
Open `output/report-dashboard.html` — each journey is PASS / FOLLOW-UP.

## Step 3 — the full loop for the Compensation widget
From the **legacy repo** dir, in `copilot`:
```
Use the /bafa-map skill on the Compensation widget (BAA/src/main/webapp/jsp/fa_compensation.jsp)
```
→ produces `output/spec.md` + screenshots. Review and commit it.

From the **business-analysis-next-ui** dir:
```
Use the /bafa-build skill to build the Compensation widget from output/spec.md, honoring CONTRACT.md
```
→ writes the React component + endpoint with the agreed `data-testid`s.

Then VERIFY (copilot will do this at the end of `/bafa-build`, or run it yourself):
```
python ~/bafa-comp-modernize/verify/parity/run_parity.py --screen widget
```
For any FOLLOW-UP, copilot fixes the component to satisfy `CONTRACT.md` and re-runs until
all journeys PASS.

## Step 4 (optional) — pin build conventions
Drop the conventions into the React repo so BUILD always follows them:
```bash
cp ~/bafa-comp-modernize/copilot-instructions.snippet.md \
   …/business-analysis-next-ui/.github/copilot-instructions.md
```

## Re-running
Any stage re-runs on demand. For VERIFY: `run_parity.py --screen <name>` (or `/bafa-verify`).
Fixtures + `auth_state.json` are reused — nothing to reconstruct.

## Tips for reliable gpt-5.4 runs
- One screen at a time. Don't ask MAP/BUILD to do the whole app.
- Let the **verify report** drive the fix loop — it's the objective signal.
- If a skill isn't picked up, `/skills reload` and confirm the `name:`==folder match.

---
Sources: GitHub Docs —
[add skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills),
[create skills](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/copilot-cli/customize-copilot/create-skills),
[custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli),
[custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).
