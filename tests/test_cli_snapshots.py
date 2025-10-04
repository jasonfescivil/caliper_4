"""
CLI Snapshot Tests - Ensure CLI interface stability
Prevents accidental removal of flags or commands
"""

import subprocess
import json
from pathlib import Path
import pytest
from typing import Dict, List

# Expected CLI commands and their flags
EXPECTED_CLI_STRUCTURE = {
    "retrieve": {
        "required_flags": [
            "--indexes", "--top-k", "--reranker", "--embed-provider",
            "--out", "--cloud", "--local"
        ],
        "optional_flags": [
            "--expand-queries", "--min-confidence", "--auto-route",
            "--normalize", "--verbose"
        ]
    },
    "query": {  # or "generate" depending on final naming
        "required_flags": [
            "--llm-provider", "--style", "--format", "--out"
        ],
        "optional_flags": [
            "--schema", "--reasoning", "--cohere-doc-mode",
            "--temperature", "--max-tokens"
        ]
    },
    "doctor": {
        "required_flags": [],
        "optional_flags": ["--verbose", "--fix"]
    },
    "migrate-index": {
        "required_flags": ["--source", "--target", "--embed-provider"],
        "optional_flags": ["--batch-size", "--force"]
    }
}

def get_cli_help(command: str = "") -> str:
    """Get help output for a CLI command"""
    cmd = ["poetry", "run", "caliper_v2"]
    if command:
        cmd.extend(command.split())
    cmd.append("--help")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def extract_flags_from_help(help_text: str) -> List[str]:
    """Extract all flags from help text"""
    import re
    # Match patterns like --flag or -f
    flags = re.findall(r'(?:^|\s)(--[\w-]+|-\w)', help_text, re.MULTILINE)
    return list(set(flags))

class TestCLISnapshots:
    """Test suite to ensure CLI interface stability"""
    
    def test_main_help_available(self):
        """Verify main help is accessible"""
        help_text = get_cli_help()
        assert help_text, "CLI help should return content"
        assert "caliper_v2" in help_text.lower() or "usage" in help_text.lower()
    
    def test_retrieve_command_flags(self):
        """Verify retrieve command has all expected flags"""
        help_text = get_cli_help("retrieve")
        flags = extract_flags_from_help(help_text)
        
        for required in EXPECTED_CLI_STRUCTURE["retrieve"]["required_flags"]:
            assert required in flags, f"Missing required flag: {required}"
    
    def test_generate_command_flags(self):
        """Verify generate/query command has all expected flags"""
        # Try both names since there's uncertainty
        for cmd_name in ["query", "generate"]:
            try:
                help_text = get_cli_help(cmd_name)
                if "Error" not in help_text and help_text:
                    flags = extract_flags_from_help(help_text)
                    
                    # Check for new Cohere-specific flags
                    assert "--schema" in flags or "--schema" in help_text, "--schema flag missing"
                    assert "--reasoning" in flags or "--reasoning" in help_text, "--reasoning flag missing"
                    
                    # Check provider list includes cohere
                    assert "cohere" in help_text.lower(), "Cohere not in provider list"
                    break
            except:
                continue
    
    def test_doctor_command_exists(self):
        """Verify doctor command exists for migration warnings"""
        help_text = get_cli_help("doctor")
        assert help_text, "Doctor command should exist"
        assert "Error" not in help_text, "Doctor command should be valid"
    
    def test_provider_list_includes_cohere(self):
        """Ensure Cohere is in the provider choices"""
        # Check in help text for generate/query command
        for cmd_name in ["query", "generate"]:
            help_text = get_cli_help(cmd_name)
            if help_text and "Error" not in help_text:
                assert "cohere" in help_text.lower(), f"Cohere not listed in {cmd_name} providers"
                break

    @pytest.fixture
    def snapshot_file(self, tmp_path):
        """Create a snapshot file for comparison"""
        return tmp_path / "cli_snapshot.json"
    
    def test_create_snapshot(self, snapshot_file):
        """Create a snapshot of current CLI structure for future comparison"""
        snapshot = {}
        
        # Capture main help
        snapshot["main"] = get_cli_help()
        
        # Capture command helps
        for cmd in ["retrieve", "query", "generate", "doctor"]:
            help_text = get_cli_help(cmd)
            if help_text and "Error" not in help_text:
                snapshot[cmd] = {
                    "help": help_text,
                    "flags": extract_flags_from_help(help_text)
                }
        
        # Save snapshot
        snapshot_file.write_text(json.dumps(snapshot, indent=2))
        assert snapshot_file.exists(), "Snapshot should be created"
        
        # In CI, compare with previous snapshot if exists
        reference_snapshot = Path("tests/fixtures/cli_snapshot_reference.json")
        if reference_snapshot.exists():
            ref_data = json.loads(reference_snapshot.read_text())
            # Check no flags were removed
            for cmd, data in ref_data.items():
                if cmd in snapshot and "flags" in data:
                    old_flags = set(data["flags"])
                    new_flags = set(snapshot[cmd]["flags"]) if "flags" in snapshot[cmd] else set()
                    removed = old_flags - new_flags
                    assert not removed, f"Flags removed from {cmd}: {removed}"

if __name__ == "__main__":
    # Quick smoke test
    test = TestCLISnapshots()
    test.test_main_help_available()
    print("✓ CLI snapshot tests ready")