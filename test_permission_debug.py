#!/usr/bin/env python3
"""Debug script to test permission issues in Dash UI"""

from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_directory_creation():
    """Test directory creation scenarios that might cause permission errors"""
    print("Testing directory creation scenarios...")
    
    # Test current directory
    current = Path(".")
    print(f"Current directory: {current.resolve()}")
    
    # Test the paths used in the Dash app
    try:
        from caliper_v2.core.config import settings
        data_dir = Path(getattr(settings, "data_dir", Path("data_v2"))).resolve()
        outputs_dir = Path(getattr(settings, "output_dir", Path("outputs"))).resolve()
        print(f"Data dir: {data_dir}")
        print(f"Outputs dir: {outputs_dir}")
    except Exception as e:
        print(f"Settings import failed: {e}")
        data_dir = Path("data_v2").resolve()
        outputs_dir = Path("outputs").resolve()
        print(f"Using fallback - Data dir: {data_dir}")
        print(f"Using fallback - Outputs dir: {outputs_dir}")
    
    # Test _ensure_dir function
    def _ensure_dir(p: Path) -> Path:
        print(f"Testing _ensure_dir for: {p} (resolved: {p.resolve()})")
        if p.resolve() != Path(".").resolve():
            print(f"  Creating directory (not current dir)")
            try:
                p.mkdir(parents=True, exist_ok=True)
                print(f"  SUCCESS: Created {p}")
            except Exception as e:
                print(f"  ERROR: Failed to create {p}: {e}")
        else:
            print(f"  SKIPPED: Would not create current directory")
        return p
    
    # Test the specific paths used in review tab
    ctx_dir = _ensure_dir(data_dir / "context")
    reviews_dir = _ensure_dir(outputs_dir / "reviews")
    drafts_dir = _ensure_dir(outputs_dir / "drafts")
    
    # Test file path scenarios that might cause issues
    test_paths = [
        "output.json",  # Simple filename
        "review_000000.json",  # Default review filename
        str(reviews_dir / "review_000000.json"),  # Full path
    ]
    
    for test_path in test_paths:
        p = Path(test_path)
        print(f"\nTesting path: {test_path}")
        print(f"  Path object: {p}")
        print(f"  Parent: {p.parent}")
        print(f"  Parent resolved: {p.parent.resolve()}")
        print(f"  Is parent current dir? {p.parent == Path('.')}")
        print(f"  Is parent resolved current dir? {p.parent.resolve() == Path('.').resolve()}")
        
        # Test the mkdir logic
        try:
            if p.parent != Path("."):
                print(f"  Would create parent directory: {p.parent}")
            else:
                print(f"  Would NOT create parent directory (current dir)")
        except Exception as e:
            print(f"  ERROR testing mkdir logic: {e}")

def test_review_command_import():
    """Test importing the review command to see if that causes issues"""
    print("\nTesting review command import...")
    try:
        from caliper_v2.commands import review as review_cmd
        print("SUCCESS: review command imported")
        
        # Test the _write_json and _write_text functions
        print("Testing _write_json function...")
        test_data = {"test": "data"}
        test_path = Path("test_output.json")
        
        # This should use our fixed version
        review_cmd._write_json(test_path, test_data)
        print(f"SUCCESS: _write_json worked, created {test_path}")
        
        # Clean up
        if test_path.exists():
            test_path.unlink()
            print("Cleaned up test file")
            
    except Exception as e:
        print(f"ERROR importing or testing review command: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Permission Debug Test ===")
    test_directory_creation()
    test_review_command_import()
    print("=== Test Complete ===")