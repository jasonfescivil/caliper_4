# Documentation Maintenance Plan

This document outlines the guidelines, processes, and standards for maintaining Caliper v2 documentation.

## Documentation Structure Overview

```
docs/
├── index.md                    # Central documentation index
├── user/                       # User-facing guides
├── developer/                  # Development and API documentation  
├── reference/                  # Command reference and API specs
├── workflows/                  # Specific workflow guides
├── reviews/                    # Code reviews and assessments
└── technical/                  # Technical implementation details
```

## File Naming Conventions

### Standardized Naming Pattern
- Use **kebab-case** for all file names (e.g., `installation-guide.md`)
- Be descriptive and specific (e.g., `dash-ui-guide.md` not `ui.md`)
- Use consistent suffixes:
  - `-guide.md` for how-to documentation
  - `-reference.md` for technical references
  - `-overview.md` for architectural or conceptual content
  - `-workflow.md` for process documentation

### Directory Organization
- **user/**: End-user guides and tutorials
- **developer/**: Development setup, coding standards, architecture
- **reference/**: API documentation, command references
- **workflows/**: Step-by-step process guides
- **reviews/**: Code reviews, assessments, planning documents
- **technical/**: Implementation details, migration guides

## Recent Cleanup Activities (September 2024)

### Root Directory Cleanup
The root directory was significantly cleaned up to maintain a professional repository structure. The following actions were taken:

**Files moved to `scripts/` directory:**
- `build_all_sources_graph.ps1` - Graph building automation
- `fetch_external_repos.ps1` - External repository fetching
- `inspect_all.ps1` & `inspect_all_print.ps1` - Inspection utilities
- `test_providers.ps1` & `test_crosswalk_providers.ps1` - Provider testing
- `convert_docx_to_md.py` & `convert_docx_to_md_improved.py` - Document conversion
- `enable_hybrid.py` - Hybrid search enablement
- `improve_spore.py` - Spore enhancement utility
- `format_judgment_report.py` - Report formatting utility
- `test_cohere_quick.py` & `test_frontier_models.py` - Provider testing
- `run_caliper_v2.py` - CLI wrapper utility

**Files relocated to appropriate directories:**
- `WARP.md` → `docs/developer/warp-integration-guide.md`
- `test_q.txt` → `prompts/test_q.txt`
- `Tekoa Facility Plan draft v2 (2).docx` → `data/documents/Tekoa_Facility_Plan_draft_v2.docx`

**Files removed:**
- `docker-compose.yml.bck` (outdated backup)
- `augment_assessment_proposal` (temporary file)

**Final root directory structure:**
- `docker-compose.yml`, `Dockerfile` - Containerization
- `poetry.lock`, `pyproject.toml` - Python project configuration
- `README.md` - Main project documentation
- All hidden files (`.env`, `.gitignore`, etc.) - Configuration

This cleanup ensures the root directory only contains essential project configuration files and maintains a clean, professional appearance.

## Content Guidelines

### Writing Standards
- Use clear, concise language
- Structure with proper Markdown headers (H1, H2, H3)
- Include code examples with proper syntax highlighting
- Provide cross-references to related documentation
- Use consistent terminology throughout

### Required Sections
For user guides:
- Overview/Purpose
- Prerequisites
- Step-by-step instructions
- Examples
- Troubleshooting (if applicable)

For developer documentation:
- Purpose and scope
- Technical requirements
- Implementation details
- Code examples
- Testing information

### Code Examples
- Always use proper syntax highlighting
- Include complete, runnable examples when possible
- Use realistic, project-specific examples
- Test all code examples regularly

## Review Process

### Documentation Changes
1. **Minor updates** (typos, clarifications): Direct commit to main
2. **Structural changes** (new sections, reorganization): Create PR for review
3. **New documentation**: Create PR with at least one reviewer

### Review Checklist
- [ ] Content accuracy and completeness
- [ ] Consistent formatting and style
- [ ] Proper cross-references and links
- [ ] Code examples tested and working
- [ ] File naming follows conventions
- [ ] Appropriate directory placement

## Version Control

### Git Practices
- Use conventional commit messages for documentation changes:
  - `docs: add installation guide for WSL`
  - `docs: update command reference for v2.1`
  - `docs: fix broken links in developer guides`

### Tracking Changes
- Document breaking changes in relevant guides
- Update version-specific information when releases occur
- Maintain changelog for significant documentation updates

## Quality Assurance

### Regular Maintenance Tasks

#### Monthly Reviews
- [ ] Check all external links for validity
- [ ] Verify code examples still work with current codebase
- [ ] Update screenshots and UI references if needed
- [ ] Review and update version-specific information

#### Quarterly Assessments
- [ ] Audit documentation structure for improvements
- [ ] Identify and eliminate redundant content
- [ ] Survey users for documentation feedback
- [ ] Plan documentation improvements for next quarter

#### Release-Triggered Updates
- [ ] Update installation and setup guides
- [ ] Revise command references for new/changed commands
- [ ] Update workflow guides for process changes
- [ ] Add migration guides if necessary

### Content Validation

#### Automated Checks
- Link validation (consider tools like `markdown-link-check`)
- Spelling and grammar checking
- Code example testing in CI/CD

#### Manual Validation
- Walkthrough of user guides with fresh environment
- Developer guide validation with new team members
- Cross-reference verification

## Deprecation Process

### Outdated Documentation
1. **Identify**: Mark outdated content during reviews
2. **Migrate**: Move valuable content to updated documents
3. **Archive**: Move deprecated files to `archive/` directory
4. **Clean**: Remove completely obsolete files after migration

### Communication
- Announce documentation changes in team communications
- Update central index when structure changes
- Provide migration guides for significant reorganizations

## Style Guide

### Markdown Standards
- Use consistent header hierarchy (H1 for titles, H2 for major sections)
- Use proper list formatting (consistent indentation)
- Include blank lines around headers and code blocks
- Use `**bold**` for emphasis, `*italics*` for definitions

### Code Formatting
```bash
# Good: Use syntax highlighting
poetry run caliper_v2 --help
```

```
# Avoid: No syntax highlighting for code
poetry run caliper_v2 --help
```

### Cross-References
- Use relative paths for internal links: `[Installation Guide](../user/installation-guide.md)`
- Always verify links after moving files
- Use descriptive link text, not generic phrases like "click here"

## Tools and Automation

### Recommended Tools
- **Markdown editors**: VSCode with Markdown extensions, Obsidian
- **Link checking**: `markdown-link-check`, manual verification
- **Spell checking**: Built-in editor features, `cspell` for automation
- **Structure validation**: Custom scripts to verify naming conventions

### Automation Opportunities
- Pre-commit hooks for link checking
- Automated link validation in CI/CD
- Spell checking in pull requests
- Documentation coverage reports

## Responsibilities

### Development Team
- Update relevant documentation when making code changes
- Review documentation PRs for technical accuracy
- Provide feedback on documentation usability

### Documentation Maintainers
- Regular audits and cleanup
- Structure improvements and reorganization
- Style guide enforcement
- Tool evaluation and implementation

### Contributors
- Follow established conventions
- Test instructions before submitting
- Request clarification when documentation is unclear
- Suggest improvements for user experience

## Metrics and Success Criteria

### Quality Metrics
- Documentation coverage (% of features documented)
- Link health (% of working internal/external links)
- Freshness (last update dates, relevance to current version)
- User feedback scores and issue reports

### Success Indicators
- Reduced support questions about well-documented features
- Faster onboarding for new developers
- Positive feedback on documentation clarity
- Consistent documentation structure across all areas

## Contact and Support

For documentation-related questions or suggestions:
- Create issues with `documentation` label
- Include specific improvement suggestions
- Reference the relevant documentation files
- Provide context about your use case

---

*Last updated: 2024-12-19*  
*Next review due: 2025-03-19*