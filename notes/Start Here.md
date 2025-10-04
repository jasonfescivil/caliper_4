# Start Here

This vault lives at `C:\\repos\\caliper` and follows a light, pragmatic structure for project notes.

## Conventions
- Folder prefixes: `00_`..`90_` to keep views ordered (no PARA reorg).
- Properties: use minimal front matter on most notes:
  - `type: note|project|area|resource|meeting|decision|person`
  - `status: inbox|active|waiting|done|archived` (as needed)
  - `created`, `updated`, `owner`, `related`
- Attachments: set Obsidian → Files & Links → Default location → “In subfolder under current folder” named `_assets`.
- People: create one note per person/org in `notes/60_people/` using the People template; link them with `[[Name]]`.

## Folders (numbered)
- `00_todos/` quick capture and triage
- `10_dashboards/` Home, Projects, Decisions, People, Caliper Ops
- `20_daily/` ISO daily notes `YYYY-MM-DD`
- `30_projects/` project hubs + local assets
- `40_proposals/` proposals (active or reference)
- `50_decisions/` index/roll‑up of per‑project decision logs
- `60_people/` one note per person/org
- `80_outputs/` generated outputs
- `90_templates/` templates for Templater/core Templates

## Templates
Set Templates → folder location to `notes/90_templates/` and use:
- Project Hub.md, Meeting.md, Reference.md, Decision Log.md
- People.md (for `notes/60_people/`)

## Dashboards
Open and bookmark:
- `notes/10_dashboards/Home.md` (tasks, active projects, waiting)
- `notes/10_dashboards/Projects.md`, `Decisions.md`, `People.md`, `Caliper Ops.md`

## Cleanup scripts
- PowerShell: `./scripts/cleanup_sweeper.ps1 [-Execute]`
- Bash/WSL: `bash scripts/cleanup_sweeper.sh [--execute]`

Keep the repo tidy by running a dry‑run first; review the plan in `logs/`.
