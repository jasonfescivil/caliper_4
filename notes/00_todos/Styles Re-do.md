Awesome—let’s blend the staged style/template refactor with your Obsidian setup so you stay productive **today** and grow it cleanly later. I’ll keep the same Stage 0→6 rhythm, but each stage now ships tiny Obsidian pieces (notes, dashboards, templates) that auto-document what you’ve built.

# Stage 0 (today, 30–60 min): centralize style text + stand up the vault

**Code (no behavior change)**

- Add `src/caliper_v2/prompting/style_engine.py` with the tiny `style_guidance(...)` helper.
    
- Replace the 3 `if/elif` style blocks with `style_guidance(...)`.
    
- Optional CLI: `caliper styles` to list built-ins.
    

**Obsidian (fast wins)**

- Make **`C:\repos\caliper`** your vault.  
    Exclude folders in Obsidian: `data_v2, .venv, logs, .ruff_cache, .mypy_cache, knowledge_base (optional), outputs (optional)`.
    
- Create:
    
    - `notes/READMEs/README_local_quickstart.md` (link from `README.md`).
        
    - `notes/prompting/STYLE_CATALOG.md` — a human-readable page that briefly describes each style.
        
    - `notes/dashboards/Dev-Daily.md` — your daily checklist (activate venv, run doctor, etc.).
        
- Paste these seed sections (you can refine later):
    

**STYLE_CATALOG.md (seed)**

```
# Style Catalog (live)
- strict-citation — terse, exact labels
- quote-heavy — short, high-signal quotes
- compare — key points + side-by-side + conclusion
- outline — nested bullets focusing on headings/sections
- best — clear bullets + brief quotes, include labels when present
```

**Dev-Daily.md (seed)**

```
- [ ] Open terminal in C:\repos\caliper
- [ ] .\.venv\Scripts\activate
- [ ] python run_caliper_v2.py doctor
- [ ] Trial run: caliper generate --style strict-citation "..."
- [ ] Jot notes / issues below

### Notes / Issues
```

> Ship this today. You’re already using styles and documenting them in one place.

---

# Stage 1 (today/tomorrow): one prompt builder + light task templates

**Code**

- Add `src/caliper_v2/prompting/prompt_builder.py` with `TaskTemplate` + `build_prompt(...)`.
    
- Switch `generate`, `query`, and `_synthesize_with_style` to call `build_prompt(...)` (defaults match current behavior).
    

**Obsidian**

- Create `notes/prompting/TASK_TEMPLATES.md` describing the three tasks (Generate, Query, Synthesize) in plain English.
    
- Add a tiny CLI to **export** the current styles list to Obsidian:
    

```python
# src/caliper_v2/cli_styles.py
@cli.command("styles-export")
def styles_export():
    from caliper_v2.prompting.style_engine import _STYLE_TEXT
    out = ["# Style Catalog (auto-generated)\n"]
    for name, lines in _STYLE_TEXT.items():
        out += [f"## {name}", "", *[f"- {ln}" for ln in lines], ""]
    Path("notes/prompting/STYLE_CATALOG.md").write_text("\n".join(out), encoding="utf-8")
    print("Exported to notes/prompting/STYLE_CATALOG.md")
```

- Add a **dashboard** that shows “what changed”:
    
    - `notes/dashboards/Prompting.md` → link to `STYLE_CATALOG.md` and `TASK_TEMPLATES.md`.
        
    - Keep a short **Decision Log**: `notes/decisions/0001-style-engine-stage1.md` with what/why.
        

---

# Stage 2 (this week): structured styles (dataclass) but **inline** (no YAML yet)

**Code**

- Replace string styles with the small `@dataclass Style` (fields for tone/structure/citations/quotes) and `to_lines()`.
    
- Keep `style_guidance(style, fallback)` as the only call site, so no churn elsewhere.
    

**Obsidian**

- Upgrade `styles-export` to emit **per-style** notes:
    
    - Write `notes/prompting/styles/<name>.md` with frontmatter like:
        
        ```
        ---
        style: strict-citation
        tone: concise
        structure: numbered_bullets
        citations: inline_index
        page_labels: always
        quotes_allowed: false
        ---
        ```
        
    - Your `STYLE_CATALOG.md` can just link to each style file.
        
- Add `notes/dashboards/Styles-Index.md` with a simple list of links (no Dataview needed yet).
    

---

# Stage 3 (next): style **composition** and ad-hoc overrides (still no YAML)

**Code**

- Add `compose_styles("compare+strict-citation")`.
    
- Optional: `--set citations.include_page_labels=always` overrides via a tiny keypath parser.
    
- Enforce task invariants in `build_prompt` (e.g., `query/synth` force inline `[n]` citations).
    

**Obsidian**

- `notes/decisions/0002-style-composition-defaults.md` — record your default composition per task (e.g., `generate: best`, `query: strict-citation`).
    
- Update the exporter to include a **“Compositions”** section in `STYLE_CATALOG.md` with the default pairs you use day-to-day.
    

---

# Stage 4 (when ready): optional YAML loader + Obsidian authoring

**Code**

- Make YAML support an **optional extra**. If `pyyaml` missing, skip YAML and log a friendly note.
    
- Load order: built-ins → `styles/styles.yaml` (repo) → `~/.caliper/styles/*.yaml` (user) with overrides.
    

**Obsidian**

- Author styles in `notes/prompting/styles/` first; when stable, mirror to `styles/styles.yaml`.  
    (Keep human docs in Obsidian; machine config in `styles/`.)
    
- If you install **Obsidian Git** later, commit notes without heavy dirs. Your vault remains the repo root.
    

---

# Stage 5 (later): adherence checker + Obsidian dashboard

**Code**

- Add a post-gen checker:
    
    - `structure=numbered_bullets` → ensure lines match `^\d+[\.\)]`.
        
    - `citations=inline_index` → ensure `\[\d+\]` appears.
        
    - Log warnings to `logs/style_adherence/<date>.log`.
        
- Optional `--enforce-style` to auto-retry once with a corrective note.
    

**Obsidian**

- Create `notes/dashboards/Style-Adherence.md` with a quick “paste logs here” section OR point to `logs/`.
    
- If you prefer Dataview, drop a tiny script to mirror last N log lines into `notes/dashboards/_ingest/`—but keep it optional to avoid complexity.
    

---

# Stage 6 (nice-to-have): model adapters

**Code**

- Add a tiny “adapter” layer that tweaks phrasing per LLM vendor.
    
- Keep docs in `notes/prompting/MODEL_ADAPTERS.md` explaining differences.
    

**Obsidian**

- Add a **Decision** note when you pick defaults per vendor.
    

---

## Repo & Obsidian glue that keeps you fast (today)

- Stick with the repo shape you already planned:
    
    ```
    C:\repos\caliper
      ├─ src/
      ├─ scripts/
      ├─ notes/                # Obsidian lives here
      │   ├─ READMEs/
      │   ├─ prompting/
      │   │   └─ styles/
      │   ├─ dashboards/
      │   ├─ decisions/
      │   └─ todos/
      ├─ outputs/              # large artifacts; link to from notes/outputs records
      ├─ notebooks/            # Jupyter/Colab (optional render in Obsidian)
      ├─ logs/
      ├─ styles/               # (Stage 4+) YAML config lives here
      ├─ .env  .gitignore  requirements.heavy.txt  README.md
    ```
    
- **Outputs:** for each important run, create a short `notes/outputs/<slug>-<date>.md` “output record” that links to the artifact in `outputs/`. Template:
    

```
# Output: <topic> — <YYYY-MM-DD>
- Command: `caliper generate --style strict-citation "..." `
- Inputs: <brief>
- Key citations: <brief>
- File: [[../../outputs/<slug>/<file>.md]]
- Issues: <short bullets>
```

- **Environment doc:** keep `notes/READMEs/README_local_quickstart.md` authoritative. If anything about env changes, update this note first.
    

---

## Your “today” checklist (copy/paste)

1. Make `C:\repos\caliper` the Obsidian vault; exclude heavy dirs.
    
2. Create `notes/READMEs/README_local_quickstart.md`, `notes/prompting/STYLE_CATALOG.md`, `notes/dashboards/Dev-Daily.md`.
    
3. Add `style_engine.py`; replace the three blocks with `style_guidance(...)`.
    
4. Add `caliper styles` and (optional) `caliper styles-export` to regenerate `STYLE_CATALOG.md`.
    
5. Test: run one `generate`, one `query`, one agent synth with your usual prompts. Jot issues in `Dev-Daily.md`.
    

That’s it—you’ll be using styles + Obsidian **today**, with zero dependency drama and a clear lane to richer features later.