Below is a simple, durable Obsidian setup that works for **any** kind of project (work, personal, research) without heavy plugins or complexity. It’s based on practices common among approachable Obsidian power users and the official docs.

---

## What experienced (but not extreme) Obsidian users agree on

- **Keep folders simple; let links, tags, and Search do the heavy lifting.** People often use a minimal folder layout (or PARA) and rely on links and saved searches to surface what they need. ([Obsidian Forum](https://forum.obsidian.md/t/folders-vs-linking-vs-tags-the-definitive-guide-extremely-short-read-this/78468?utm_source=chatgpt.com "Folders vs. linking vs. tags—the definitive guide (extremely ..."), [Forte Labs](https://fortelabs.com/blog/para/?utm_source=chatgpt.com "The PARA Method: The Simple System for Organizing Your ..."))
    
- **Use one main vault unless you have strict boundaries (e.g., work vs. personal).** A vault is just a folder; one-vault maximizes linking, multiple vaults are for hard separation. ([Obsidian Help](https://help.obsidian.md/vault?utm_source=chatgpt.com "Create a vault"), [Steph Ango](https://stephango.com/vault?utm_source=chatgpt.com "How I use Obsidian"), [Reddit](https://www.reddit.com/r/ObsidianMD/comments/pnshee/multiple_vaults/?utm_source=chatgpt.com "Multiple vaults ? : r/ObsidianMD"))
    
- **Name things consistently using ISO dates (`YYYY-MM-DD`).** It sorts well and plays nicely with Obsidian’s Daily Notes. ([Obsidian Help](https://help.obsidian.md/plugins/daily-notes?utm_source=chatgpt.com "Daily notes"), [Obsidian Forum](https://forum.obsidian.md/t/daily-notes-naming-conventions-iso8601/55267?utm_source=chatgpt.com "Daily Notes naming conventions ISO8601 - Help"))
    
- **Use Properties for structured metadata, tags for quick facets.** Properties (the UI for front matter) are first‑class in Obsidian search; tags are great for light categorization. ([Obsidian Help](https://help.obsidian.md/properties?utm_source=chatgpt.com "Properties"))
    
- **Templates (core plugin) are enough for most users.** Start with the built‑in Templates; add “Templater” only if you need scripting. ([Obsidian Help](https://help.obsidian.md/plugins/templates "Templates - Obsidian Help"), [Reddit](https://www.reddit.com/r/ObsidianMD/comments/z917by/obsidian_templates/?utm_source=chatgpt.com "Obsidian templates : r/ObsidianMD"))
    
- **Embed searches to create live dashboards without plugins.** Search supports operators (including tasks) and can be embedded right in a note. ([Obsidian Help](https://help.obsidian.md/plugins/search "Search - Obsidian Help"))
    
- **Pick a sane attachment rule and stick to it.** Obsidian lets you set where attachments land—e.g., an `_assets` subfolder next to each note. ([Obsidian Help](https://help.obsidian.md/attachments?utm_source=chatgpt.com "Attachments"))
    
- **Bookmarks (core) replace the old ‘Starred’ and can save searches.** Great for pinning project hubs and dashboards. ([Obsidian Help](https://help.obsidian.md/plugins/bookmarks?utm_source=chatgpt.com "Bookmarks"), [Obsidian Forum](https://forum.obsidian.md/t/starred-plug-in-has-gone-away/59487?utm_source=chatgpt.com "Starred plug-in has gone away! - Help"))
    
- Optional: **MOCs (Maps of Content)** make human‑curated “maps” for topics; use them sparingly. ([LYT Kit](https://notes.linkingyourthinking.com/Cards/MOCs%2BOverview?utm_source=chatgpt.com "MOCs Overview"))
    

---

## The system (vault → folders → notes → tags → templates)

### 1) Vault level

- **Use one main vault** named after you or your org. Create a second vault only if you must keep data completely separate (e.g., employer policy). A vault is just a folder on disk that Obsidian indexes. ([Obsidian Help](https://help.obsidian.md/vault?utm_source=chatgpt.com "Create a vault"))
    

### 2) Folder layout (simple PARA + Daily + People + Templates)

Create these top‑level folders (the numbers keep them ordered):

```
00_Inbox/
10_Projects/            # Active, outcome-based work
20_Areas/               # Ongoing responsibilities (Finance, HR, Health…)
30_Resources/           # Reference, topics, learnings
40_Archive/             # Completed/closed items
Daily/                  # Daily notes (optional but helpful)
People/                 # One note per person/org you interact with
Templates/              # Template files for the core Templates plugin
```

**Rules:**

- A _project_ gets a subfolder under `10_Projects` with a single **Project Hub** note inside.
    
- Use `40_Archive` to park finished projects or stale areas—don’t delete. PARA is built for cross‑tool consistency and fast retrieval. ([Forte Labs](https://fortelabs.com/blog/para/?utm_source=chatgpt.com "The PARA Method: The Simple System for Organizing Your ..."))
    
- Set attachments to **“In subfolder under current folder”** and name it `_assets`. This keeps each project’s files (images, PDFs, Office docs) beside their notes, which many users prefer for project work. `Settings → Files & Links → Default location for new attachments → In subfolder under current folder` (folder name: `_assets`). ([Obsidian Help](https://help.obsidian.md/attachments?utm_source=chatgpt.com "Attachments"))
    

> Alternative if you prefer one bucket: create `_attachments/` at the vault root and set attachments there (trade‑off: less “locality” per project). ([Obsidian Help](https://help.obsidian.md/attachments?utm_source=chatgpt.com "Attachments"))

### 3) Naming & note titles

- **Daily notes:** `YYYY-MM-DD` (e.g., `2025-08-18`). ([Obsidian Help](https://help.obsidian.md/plugins/daily-notes?utm_source=chatgpt.com "Daily notes"))
    
- **Meetings:** `YYYY-MM-DD - Meeting - Person/Org - Topic`
    
- **Project hubs:** `Project - ShortName` (lives in that project’s folder)
    
- **General notes:** clear noun phrase (avoid cleverness).  
    Using ISO dates gives you natural sorting across platforms. ([Obsidian Forum](https://forum.obsidian.md/t/daily-notes-naming-conventions-iso8601/55267?utm_source=chatgpt.com "Daily Notes naming conventions ISO8601 - Help"))
    

### 4) Properties (front matter) and tags

Keep it minimal and consistent.

**Core Properties (use on most notes):**

```yaml
---
type: note|project|area|resource|meeting|decision
status: inbox|active|waiting|done|archived
created: {{date:YYYY-MM-DD}}
updated:
related:
owner:
---
```

- **Use `type` and `status` as searchable Properties** (first‑class in Search). Keep values lowercase. ([Obsidian Help](https://help.obsidian.md/plugins/search "Search - Obsidian Help"))
    
- **Prefer wiki‑links to People notes** over people tags (e.g., `[[Alex Rivera]]`), then you can open that person’s page and see backlinks. ([Obsidian Help](https://help.obsidian.md/plugins/backlinks?utm_source=chatgpt.com "Backlinks - Obsidian Help"))
    

**Tags (sparingly):**

- `#topic/...` for subject matter (e.g., `#topic/wastewater`),
    
- `#type/...` if you _don’t_ put `type` in Properties,
    
- `#status/...` only if you prefer tags over `status` property (don’t duplicate both).
    

Official guidance: tags are keywords; Properties capture structured data. Use both purposefully. ([Obsidian Help](https://help.obsidian.md/tags?utm_source=chatgpt.com "Tags - Obsidian Help"))

---

## Templates to build (core Templates plugin)

> Enable **Settings → Core plugins → Templates**. Set `Template folder location` to `Templates/`. Variables: `{{title}}`, `{{date}}`, `{{time}}` (format with Moment tokens). ([Obsidian Help](https://help.obsidian.md/plugins/templates "Templates - Obsidian Help"))

### A) Project Hub template (`Templates/Project Hub.md`)

```markdown
---
type: project
status: active
owner:
created: {{date:YYYY-MM-DD}}
updated:
related:
---

# {{title}}  <!-- e.g., Project - Website Refresh -->

**Outcome:**  
**Scope / Non-goals:**  
**Deadline:**  

## Links
- Repo / Folder: 
- Spec / Brief: 
- Stakeholders: [[Person A]], [[Person B]]

## Next actions
- [ ] 

## Notes
- 

## Decisions
- See: [[Decisions - {{title}}]]

## References
- 
```

### B) Meeting note (`Templates/Meeting.md`)

```markdown
---
type: meeting
status: done
created: {{date:YYYY-MM-DD}}
participants: [[Person A]], [[Person B]]
project:
---

# {{title}}  <!-- e.g., 2025-08-18 - Meeting - ABC Utilities - Grant scope -->

**Agenda**
- 

**Notes**
- 

**Actions**
- [ ] Owner – task @due(YYYY-MM-DD)

**Follow-ups**
- 
```

### C) Knowledge/Reference note (`Templates/Reference.md`)

```markdown
---
type: resource
status: active
created: {{date:YYYY-MM-DD}}
aliases:
related:
---

# {{title}}

## Summary
- 

## Key points
- 

## Sources
- 
```

### D) Decision log (per project) (`Templates/Decision Log.md`)

```markdown
---
type: decision
status: active
created: {{date:YYYY-MM-DD}}
project:
---

# Decisions – {{title}}

> Keep decisions short and dated. Link to the note where context lives.

- **{{date:YYYY-MM-DD}} – Decision:** 
  - **Context:** [[Related Note]]
  - **Implication:** 
```

### E) Daily note (`Templates/Daily.md`)

```markdown
---
type: daily
created: {{date:YYYY-MM-DD}}
---

# {{title}}  <!-- will be the date -->
## Plan
- [ ] 

## Notes / Scratch
- 

## Done
- [x] 
```

---

## Saved searches & lightweight dashboards (no plugins)

Create a **Home** note and embed live queries:

````markdown
## Open tasks anywhere
```query
task-todo:
````

## Active projects

```query
[type:project] [status:active]
```

## Waiting items

```query
[type:project] [status:waiting] OR tag:#status/waiting
```

## Notes mentioning [[Person A]]

```query
"[[Person A]]"
```

```

Tips:
- Search operators include `task:`, `task-todo:`, `task-done:` and property lookups like `[status:active]`. You can embed those searches in notes using a `query` code block. :contentReference[oaicite:19]{index=19}  
- Bookmark the Home note and your most‑used searches with the **Bookmarks** core plugin (you can bookmark files, folders *and* searches). :contentReference[oaicite:20]{index=20}

---

## “Start here” — 20‑minute setup

1) **Make folders** exactly as shown above and add an `_assets` subfolder rule for attachments (subfolder under current folder). :contentReference[oaicite:21]{index=21}  
2) **Turn on core plugins:** Templates, Daily notes, Search, Backlinks, Bookmarks. :contentReference[oaicite:22]{index=22}  
3) **Create templates** (paste the ones above into `Templates/`). Set Templates → folder location. :contentReference[oaicite:23]{index=23}  
4) **Create two notes:**  
   - `Home` (embed the queries above),  
   - `Start Here` (explain your rules to your future self).  
5) **Create your first project** in `10_Projects/` using the Project Hub template.  
6) **Use Daily notes** when you’re in motion; link or move anything worth keeping into the right project/area later. :contentReference[oaicite:24]{index=24}

---

## Maintenance habits

- **Triage the Inbox weekly:** move items to a project/area or delete. (PARA favors fast, lightweight filing.) :contentReference[oaicite:25]{index=25}  
- **Close or re‑activate** projects by flipping `status` and moving the folder to `40_Archive` when done. :contentReference[oaicite:26]{index=26}  
- **Keep tags lean;** prune or unify similar tags monthly. :contentReference[oaicite:27]{index=27}

---

## Optional, when you’re ready

- **Tasks plugin** (community) if you need due dates, recurring tasks, queries, etc. The plugin tracks checklists across your vault and is well‑documented. (Nice upgrade—but start simple.) :contentReference[oaicite:28]{index=28}  
- **MOCs** for complex topics: create a curated “map” note that lists the best entry points on a theme. :contentReference[oaicite:29]{index=29}  
- **Starter vaults/templates to browse:**  
  - Obsidian Starter Vaults and template sets (curated examples). :contentReference[oaicite:30]{index=30}  
  - SoRobby’s “Obsidian Starter Vault” (general starter structure + templates). :contentReference[oaicite:31]{index=31}  
  - Linking Your Thinking’s Ideaverse Lite/LYT Kit (learn MOCs by clicking around; use pieces, not the whole thing). :contentReference[oaicite:32]{index=32}  
  - A fresh blog example of a **simple** folder system (FINVA) for perspective. :contentReference[oaicite:33]{index=33}

---

## Why this works

- Minimal folders make filing fast; everything else is surfaced by backlinks, properties, tags, and embedded searches. :contentReference[oaicite:34]{index=34}  
- PARA ensures the system scales across *any* digital work, not just notes. :contentReference[oaicite:35]{index=35}  
- Sticking attachments next to notes reduces friction on real projects (screenshots, PDFs, spreadsheets). :contentReference[oaicite:36]{index=36}  
- You can set all of this up with **core** features and add plugins only to solve specific problems later. :contentReference[oaicite:37]{index=37}

---

If you want, I can generate a **starter vault zip** with this exact folder tree and the five templates pre‑filled so you can open it in Obsidian immediately.
::contentReference[oaicite:38]{index=38}
```