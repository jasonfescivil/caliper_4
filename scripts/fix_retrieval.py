"""
Automated fix for retrieval system control flow bug.

This script:
1. Backs up cli.py
2. Comments out the buggy simple cloud path (lines ~1489-1570)
3. Ensures sophisticated path runs for all cloud retrievals

Run with: python scripts/fix_retrieval.py
"""

import re
from pathlib import Path
from datetime import datetime

def backup_file(filepath: Path) -> Path:
    """Create timestamped backup of file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.with_suffix(f".backup_{timestamp}.py")
    backup_path.write_text(filepath.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"✅ Backed up to: {backup_path}")
    return backup_path

def apply_fix(filepath: Path) -> bool:
    """Apply the retrieval fix to cli.py."""
    content = filepath.read_text(encoding="utf-8")
    
    # Find the buggy section: starts with "if cloud:" and ends with "return"
    # We need to comment it out
    
    # Pattern to find the buggy block
    # Look for: "if cloud:" followed by lots of code, ending with early return before sophisticated logic
    
    # Strategy: Find the block and replace with commented version
    pattern = r'(\s+# Cloud-only: require API key and IDs\s+if cloud:.*?typer\.echo\(str\(out_path\)\)\s+return)'
    
    # Check if already fixed
    if "# BUGGY SIMPLE PATH - COMMENTED OUT" in content:
        print("⚠️  Fix already applied. Skipping.")
        return False
    
    # Find the problematic section more precisely
    # Look for the first "if cloud:" after the index_list check
    lines = content.split('\n')
    
    start_idx = None
    end_idx = None
    indent_level = None
    
    for i, line in enumerate(lines):
        # Find start: "# Cloud-only: require API key and IDs"
        if start_idx is None:
            if "# Cloud-only: require API key and IDs" in line:
                start_idx = i
                indent_level = len(line) - len(line.lstrip())
                print(f"Found buggy block start at line {i+1}")
                continue
        
        # Find end: Look for "return" after "typer.echo(str(out_path))"
        if start_idx is not None and end_idx is None:
            # Check if previous line has the echo statement
            if i > 0 and "typer.echo(str(out_path))" in lines[i-1]:
                if line.strip() == "return":
                    end_idx = i
                    print(f"Found buggy block end at line {i+1}")
                    break
    
    if start_idx is None or end_idx is None:
        print("❌ Could not find buggy block boundaries. Manual fix required.")
        print(f"   start_idx: {start_idx}, end_idx: {end_idx}")
        return False
    
    # Comment out the buggy block
    fixed_lines = lines[:start_idx]
    fixed_lines.append(" " * indent_level + "# ===== BUGGY SIMPLE PATH - COMMENTED OUT BY fix_retrieval.py =====")
    fixed_lines.append(" " * indent_level + "# This path was preventing sophisticated retrieval logic from running.")
    fixed_lines.append(" " * indent_level + "# Issues: ignores --indexes, no spore generation, no query expansion.")
    fixed_lines.append(" " * indent_level + "# The sophisticated path below handles all these correctly.")
    
    for line in lines[start_idx:end_idx+1]:
        fixed_lines.append(" " * indent_level + "# " + line)
    
    fixed_lines.append(" " * indent_level + "# ===== END COMMENTED OUT BUGGY PATH =====")
    fixed_lines.append("")
    
    # Add the rest of the file (sophisticated path)
    fixed_lines.extend(lines[end_idx+1:])
    
    # Write fixed content
    fixed_content = '\n'.join(fixed_lines)
    filepath.write_text(fixed_content, encoding="utf-8")
    
    print(f"✅ Applied fix: commented out lines {start_idx+1} to {end_idx+1}")
    return True

def verify_fix(filepath: Path) -> bool:
    """Verify the fix was applied correctly."""
    content = filepath.read_text(encoding="utf-8")
    
    checks = {
        "Backup marker present": "# ===== BUGGY SIMPLE PATH - COMMENTED OUT" in content,
        "Early return commented": "# return" in content and "typer.echo(str(out_path))" in content,
        "Sophisticated path intact": "def _sfirst_retrieve" in content,
    }
    
    all_passed = all(checks.values())
    
    print("\n📋 Verification:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all_passed

def main():
    print("🔧 Caliper Retrieval System Fix")
    print("=" * 50)
    
    # Find cli.py
    cli_path = Path("src/caliper_v2/cli.py")
    if not cli_path.exists():
        cli_path = Path("c:/repos/caliper_4/src/caliper_v2/cli.py")
    
    if not cli_path.exists():
        print("❌ Could not find cli.py")
        return 1
    
    print(f"📄 Target file: {cli_path.resolve()}")
    
    # Backup
    backup_path = backup_file(cli_path)
    
    # Apply fix
    if apply_fix(cli_path):
        # Verify
        if verify_fix(cli_path):
            print("\n✅ FIX APPLIED SUCCESSFULLY!")
            print(f"\n📝 Next steps:")
            print(f"1. Test with: poetry run python -m caliper_v2.cli retrieve \"your question\" --indexes design,federal,state --cloud --top-k 40 --out test.json")
            print(f"2. Check test.json has: indexes=[design,federal,state], spore with content, nodes from WEF")
            print(f"3. If issues, rollback with: copy {backup_path} {cli_path}")
            return 0
        else:
            print("\n⚠️  Fix applied but verification failed. Check manually.")
            print(f"Rollback: copy {backup_path} {cli_path}")
            return 1
    else:
        print("\n⚠️  No changes made.")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
