#!/usr/bin/env python3
"""
Reorganize knowledge_base with better structure and naming conventions.
Creates desktop.ini files for Directory Opus metadata.
"""

import os
import shutil
from pathlib import Path

# Define the new structure and file mappings
REORGANIZATION_PLAN = {
    "01_federal_regulations": {
        "icon": "📜",
        "description": "Federal regulations (CFR) and EPA guidance documents",
        "files": [
            (
                "federal/40 CFR 35.2120 (up to date as of 7-24-2025).pdf",
                "2025_CFR_40-35.2120_Grant_Regulations.pdf",
            ),
            (
                "federal/CFR-2014-title40-vol1-sec35-927-2.pdf",
                "2014_CFR_40-35.927-2_Grant_Amendments.pdf",
            ),
            (
                "wa_state/CFR-2023-title40-vol32-part503 Sludge Disposal.pdf",
                "2023_CFR_40-503_Biosolids_Standards.pdf",
            ),
            (
                "federal/EPA_guide-part503-biosolids-rule.pdf",
                "EPA_Guide_Part503_Biosolids_Rule.pdf",
            ),
            (
                "federal/EPA_Guide4EstimatingInfiltrationInflow.pdf",
                "EPA_Guide_Estimating_Infiltration_Inflow.pdf",
            ),
            ("federal/EPA_II_1985.pdf", "1985_EPA_Guide_Infiltration_Inflow.pdf"),
            ("federal/epa_ii_review.pdf", "EPA_Infiltration_Inflow_Review.pdf"),
            ("federal/EPA_pwm_2010.pdf", "2010_EPA_Permit_Writers_Manual.pdf"),
            ("federal/EPA_SS_EVAL_9100WGB6.pdf", "EPA_Sanitary_Sewer_Evaluation_9100WGB6.pdf"),
        ],
    },
    "02_state_regulations/washington": {
        "icon": "🏛️",
        "description": "Washington State regulations - WACs and RCWs",
        "files": [
            # WACs (Washington Administrative Code)
            ("wa_state/WAC 173-200 WQ for GW.pdf", "WAC_173-200_Water_Quality_Groundwater.pdf"),
            (
                "wa_state/WAC 173-201A WQ STD for Surface Waters.pdf",
                "WAC_173-201A_Water_Quality_Surface_Waters.pdf",
            ),
            ("wa_state/WAC 173-219 Reclaimed Water.pdf", "WAC_173-219_Reclaimed_Water_Use.pdf"),
            (
                "wa_state/WAC 173-221 Discharge Limits Domestic WW.pdf",
                "WAC_173-221_Discharge_Limits_Domestic_Wastewater.pdf",
            ),
            (
                "wa_state/WAC 173-240 WW Reports and Plans.pdf",
                "WAC_173-240_Wastewater_Submission_Plans.pdf",
            ),
            ("wa_state/WAC 173-240-050.pdf", "WAC_173-240-050_Engineering_Reports.pdf"),
            (
                "wa_state/WAC 173-308 Biosolids Management.pdf",
                "WAC_173-308_Biosolids_Management.pdf",
            ),
            # RCWs (Revised Code of Washington)
            ("wa_state/RCW 36.70A Growth Management.pdf", "RCW_36.70A_Growth_Management_Act.pdf"),
            (
                "wa_state/RCW 43.21C State Environmental Policyh.pdf",
                "RCW_43.21C_State_Environmental_Policy_Act.pdf",
            ),
            ("wa_state/RCW 90.46 Reclaimed Water Use.pdf", "RCW_90.46_Reclaimed_Water_Use.pdf"),
            (
                "wa_state/RCW 90.48 Water Pollution Control Act.pdf",
                "RCW_90.48_Water_Pollution_Control_Act.pdf",
            ),
            (
                "wa_state/RCW 90.52 Pollution Disclosure Act.pdf",
                "RCW_90.52_Pollution_Disclosure_Act.pdf",
            ),
            (
                "wa_state/RCW 90.54 Water Resources Act 1971.pdf",
                "RCW_90.54_Water_Resources_Act_1971.pdf",
            ),
            # DOE Guidance
            (
                "wa_state/DOE_Pub_9336_Industrial_Land_App_System.pdf",
                "DOE_9336_Industrial_Land_Application_Systems.pdf",
            ),
            ("wa_state/DOE_T6_Liners_Lagoons.pdf", "DOE_T6_Criteria_Liners_Lagoons.pdf"),
            ("wa_state/Ecology_96-02_Guidance.pdf", "1996_Ecology_02_Guidance_Document.pdf"),
            ("wa_state/Orange_Book.pdf", "DOE_Orange_Book_Design_Standards.pdf"),
            ("wa_state/guide.pdf", "DOE_General_Guidance.pdf"),
        ],
    },
    "05_special_districts": {
        "icon": "🏢",
        "description": "Special district regulations - PUDs, ports, water districts",
        "files": [
            # Minnesota example (move to appropriate category)
            ("federal/MN__ii_wq-wwtp5-20.pdf", "Minnesota_Infiltration_Inflow_WWTP_Guide.pdf"),
        ],
    },
    "06_design_standards/wef": {
        "icon": "📐",
        "description": "Water Environment Federation manuals and standards",
        "files": [
            (
                "WEF/wef_determining base infiltration in sewers wef coll 2007final.pdf",
                "2007_WEF_Determining_Base_Infiltration_Sewers.pdf",
            ),
            ("WEF/WEF_FD_16.pdf", "WEF_FD-16_Facilities_Design.pdf"),
            ("WEF/WEF_FD-6_SS_REHAB.pdf", "WEF_FD-6_Sanitary_Sewer_Rehabilitation.pdf"),
            ("WEF/WEF_MOP8_ch3.pdf", "WEF_MOP8_Ch3_Design_Wastewater_Treatment.pdf"),
        ],
    },
    "06_design_standards/asce": {
        "icon": "🏗️",
        "description": "American Society of Civil Engineers standards",
        "files": [
            ("Enfinger-ASCE-Pipelines-2020-Final.pdf", "2020_ASCE_Pipelines_Enfinger_Paper.pdf"),
        ],
    },
    "06_design_standards/awwa": {
        "icon": "💧",
        "description": "American Water Works Association standards",
        "files": [
            (
                "AWWD PPWTF Infiltration and Inflow Analysis Report.pdf",
                "AWWA_PPWTF_Infiltration_Inflow_Analysis.pdf",
            ),
        ],
    },
    "07_technical_reports": {
        "icon": "📊",
        "description": "Technical reports, studies, and research papers",
        "files": [
            ("522159_Fulltext.pdf", "Technical_Report_522159.pdf"),
            ("P1008BP3.pdf", "Technical_Report_P1008BP3.pdf"),
            (
                "federal/wsec-2017-fs-001-rdii-modeling-fact-sheet---final.pdf",
                "2017_WSEC_FS-001_RDII_Modeling_Factsheet.pdf",
            ),
        ],
    },
}


def create_desktop_ini(directory: Path, icon: str, description: str):
    """Create a desktop.ini file for Directory Opus metadata."""
    desktop_ini_content = f"""[.ShellClassInfo]
InfoTip={description}
IconResource=%SystemRoot%\\system32\\SHELL32.dll,3
[ViewState]
Mode=
Vid=
FolderType=Documents
Logo=
"""

    desktop_ini_path = directory / "desktop.ini"
    desktop_ini_path.write_text(desktop_ini_content, encoding="utf-8")

    # Set file attributes to hidden and system
    if os.name == "nt":  # Windows
        import subprocess

        subprocess.run(["attrib", "+h", "+s", str(desktop_ini_path)], check=False)

    # Also create a README for the directory
    readme_content = f"""# {icon} {directory.name.replace('_', ' ').title()}

{description}

## Contents

This directory contains {directory.name.replace('_', ' ')} documents.

### Naming Convention
- Federal: `[YEAR]_CFR_[PART]_[DESCRIPTION].pdf`
- State: `[TYPE]_[NUMBER]_[DESCRIPTION].pdf`
- Standards: `[YEAR]_[ORG]_[DOCUMENT]_[DESCRIPTION].pdf`

### Quick Reference
- CFR = Code of Federal Regulations
- WAC = Washington Administrative Code
- RCW = Revised Code of Washington
- EPA = Environmental Protection Agency
- DOE = Department of Ecology
- WEF = Water Environment Federation
- ASCE = American Society of Civil Engineers
- AWWA = American Water Works Association
"""

    readme_path = directory / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")


def reorganize_knowledge_base():
    """Execute the reorganization plan."""
    kb_root = Path("knowledge_base")

    # Create backup first
    print("📦 Creating backup of current structure...")
    backup_dir = kb_root.parent / "knowledge_base_backup"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    shutil.copytree(kb_root, backup_dir)
    print(f"✓ Backup created at: {backup_dir}")

    # Create new directory structure
    print("\n📁 Creating new directory structure...")
    for dir_path, info in REORGANIZATION_PLAN.items():
        new_dir = kb_root / dir_path
        new_dir.mkdir(parents=True, exist_ok=True)

        # Create desktop.ini for Directory Opus
        icon = info.get("icon", "📁")
        desc = info.get("description", "")
        if desc:
            create_desktop_ini(new_dir, icon, desc)
            print(f"✓ Created {dir_path} with metadata")

    # Move and rename files
    print("\n📄 Moving and renaming files...")
    moved_files = []

    for dir_path, info in REORGANIZATION_PLAN.items():
        for old_path, new_name in info.get("files", []):
            old_file = kb_root / old_path
            new_file = kb_root / dir_path / new_name

            if old_file.exists():
                # Ensure the parent directory exists
                new_file.parent.mkdir(parents=True, exist_ok=True)

                # Move and rename
                shutil.move(str(old_file), str(new_file))
                moved_files.append(old_path)
                print(f"✓ {old_path} → {dir_path}/{new_name}")
            else:
                print(f"⚠ File not found: {old_path}")

    # Clean up empty directories
    print("\n🧹 Cleaning up empty directories...")
    for subdir in kb_root.rglob("*"):
        if subdir.is_dir() and not any(subdir.iterdir()):
            subdir.rmdir()
            print(f"✓ Removed empty directory: {subdir.relative_to(kb_root)}")

    # Check for any unmoved files
    print("\n🔍 Checking for unmoved files...")
    all_files = list(kb_root.rglob("*.pdf")) + list(kb_root.rglob("*.txt"))
    unmoved = [f for f in all_files if str(f.relative_to(kb_root)) not in moved_files]

    if unmoved:
        print("\n⚠ The following files were not reorganized:")
        for f in unmoved:
            print(f"  - {f.relative_to(kb_root)}")

    print("\n✅ Reorganization complete!")
    print(f"📊 Moved {len(moved_files)} files into new structure")

    # Create main README
    main_readme = kb_root / "README.md"
    main_readme_content = """# 📚 Caliper Knowledge Base

## Organization Structure

This knowledge base is organized hierarchically by jurisdiction and document type:

### 📁 Directory Structure

1. **01_federal_regulations/** - Federal laws (CFR) and EPA guidance
2. **02_state_regulations/** - State-specific regulations (WAC, RCW)
3. **03_county_regulations/** - County-level ordinances
4. **04_local_municipal/** - City and town regulations
5. **05_special_districts/** - PUDs, ports, water/sewer districts
6. **06_design_standards/** - Engineering standards (WEF, ASCE, AWWA)
7. **07_technical_reports/** - Studies and research papers

### 🏷️ File Naming Convention

All files follow a consistent naming pattern for easy identification:

- **Regulations**: `[TYPE]_[NUMBER]_[DESCRIPTION].pdf`
  - Example: `WAC_173-308_Biosolids_Management.pdf`

- **Federal**: `[YEAR]_CFR_[PART]_[DESCRIPTION].pdf`
  - Example: `2023_CFR_40-503_Biosolids_Standards.pdf`

- **Standards**: `[YEAR]_[ORG]_[DOCUMENT]_[DESCRIPTION].pdf`
  - Example: `2007_WEF_Determining_Base_Infiltration_Sewers.pdf`

### 🔍 Quick Reference

- **CFR** = Code of Federal Regulations
- **EPA** = Environmental Protection Agency
- **WAC** = Washington Administrative Code
- **RCW** = Revised Code of Washington
- **DOE** = Department of Ecology (Washington)
- **WEF** = Water Environment Federation
- **ASCE** = American Society of Civil Engineers
- **AWWA** = American Water Works Association

### 💡 Usage Tips

1. Documents are organized by jurisdiction first, then by type
2. Each directory contains a README with specific contents
3. Use the naming convention to quickly identify documents
4. Desktop.ini files provide metadata for Directory Opus

---
*Last reorganized: [Date will be added by script]*
"""
    main_readme.write_text(main_readme_content, encoding="utf-8")
    print(f"\n📝 Created main README at: {main_readme}")


if __name__ == "__main__":
    reorganize_knowledge_base()
