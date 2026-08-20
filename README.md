# Daily Briefings Automation

Generates and emails daily briefings (Housing/Property/Homelessness, Tusla/Child
Protection) using the Anthropic API with web search, sent via Gmail SMTP.
Runs on a GitHub Actions schedule — no server required.

## Files

- `send_briefing.py` — generates each briefing and emails it
- `requirements.txt` — Python dependencies
- `.env.example` — template for local testing (never commit a real `.env`)
- `.github/workflows/daily-briefings.yml` — the GitHub Actions schedule
- `README.md` — this file

## One-time setup

### 1. Wipe the repo clean (recommended, since the last attempt)

Delete the existing `.github/workflows/daily-briefings.yml` (and any other
files from the last attempt) from the repo via the GitHub web UI, so there's
nothing stale left behind. It's fine to keep the repo itself — just clear it out.

### 2. Upload these 5 files using drag-and-drop, not the web editor

GitHub's inline "create new file" web editor has been unreliable for this repo
(pasted YAML has previously been committed as empty / 0 bytes). Use
drag-and-drop instead:

1. Go to your repo on github.com.
2. Click **Add file → Upload files**.
3. Drag in `send_briefing.py`, `requirements.txt`, `.env.example`, and `README.md`
   directly onto the upload area.
4. For the workflow file specifically: the path matters. On the upload page,
   drag in the **whole `.github` folder** (it contains `.github/workflows/daily-briefings.yml`)
   — modern GitHub upload accepts folders and preserves the path. If it won't
   accept a folder, instead:
   - Create the path first by clicking **Add file → Create new file**, typing
     `.github/workflows/daily-briefings.yml` as the filename (the slashes
     auto-create the folders), immediately commit that empty file, then
   - Go into the newly created file, click the pencil (edit) icon, delete any
     content, and re-upload/paste — or better, delete that placeholder file
     and drag-and-drop `daily-briefings.yml` directly into the
     `.github/workflows/` folder once it exists in the file tree.
5. Commit directly to `main`.

### 3. Verify the workflow file landed correctly

After committing, click into `.github/workflows/daily-briefings.yml` in the
GitHub UI and confirm:
- It is **not** 0 bytes / empty.
- Line 3 reads `'on':` and line 11 reads `    steps:` (indented under
  `send-briefings:`, itself indented under `jobs:`).

If either looks wrong, the paste got mangled again — delete and re-upload via
drag-and-drop rather than editing in-browser.

### 4. Add repository secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**.
Add all four:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `GMAIL_ADDRESS` | `douglas.claude.keatinge@gmail.com` |
| `GMAIL_APP_PASSWORD` | 16-character Gmail App Password (not your normal password) |
| `RECIPIENT_EMAIL` | `doug.keatinge@gmail.com` |

Gmail App Passwords: Google Account → Security → 2-Step Verification → App
Passwords. Generate one for "Mail". If it's ever lost, just generate a new one
and update the secret — the old one silently stops working.

### 5. Confirm the workflow is recognised

Go to the **Actions** tab. You should see "Daily Briefings" listed in the
sidebar (not the "browse templates" placeholder screen — that only appears
when GitHub finds zero valid workflow files, which is the symptom of the
YAML-not-committing bug).

### 6. Run it manually to test

Actions → Daily Briefings → **Run workflow** (this is the `workflow_dispatch`
trigger). Watch the run — green check means both emails sent. Click into it
if it fails; the log will show which topic failed and why.

## Schedule

Runs daily at **06:00 UTC** (07:00 Dublin time in summer/BST, 06:00 in
winter/GMT) — comfortably after the 2am-local cutoff for web search freshness,
so today's stories have had time to be published.

To change the time, edit the `cron:` line in
`.github/workflows/daily-briefings.yml` (cron is always UTC on GitHub Actions).

## YMCA briefing (not active here)

The YMCA/childcare topic is stubbed out (commented) in `send_briefing.py`'s
`TOPICS` dict. It's being configured as a separate Claude project and, when
ready, can be activated here too — either by un-commenting it (if you want it
daily) or by adding a day-of-week check in `main()` so it only runs on
Thursdays.

## Local testing

```bash
cp .env.example .env
# fill in real values in .env
pip install -r requirements.txt python-dotenv
python3 -c "from dotenv import load_dotenv; load_dotenv()" # or export vars manually
python3 send_briefing.py
```

(The GitHub Actions workflow itself doesn't need `python-dotenv` — secrets are
injected as real environment variables there.)
