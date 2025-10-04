#!/usr/bin/env python3
"""Test script to debug Dash tab loading issues"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_dash_app_initialization():
    """Test the Dash app initialization to see if it causes permission errors"""
    print("Testing Dash app initialization...")
    
    try:
        # Import the app module
        print("Importing ui_dash.app...")
        from caliper_v2.ui_dash import app
        print("SUCCESS: ui_dash.app imported")
        
        # Check if base_paths was created successfully
        if hasattr(app, 'base_paths'):
            print(f"base_paths created: {app.base_paths}")
        else:
            print("No base_paths attribute found")
            
        # Try to access the review content
        print("Accessing review_content...")
        if hasattr(app, 'review_content'):
            print("SUCCESS: review_content exists")
        else:
            print("No review_content attribute found")
            
    except Exception as e:
        print(f"ERROR during app initialization: {e}")
        import traceback
        traceback.print_exc()

def test_default_paths():
    """Test the _default_paths function specifically"""
    print("\nTesting _default_paths function...")
    
    try:
        from caliper_v2.ui_dash.app import _default_paths
        paths = _default_paths()
        print(f"SUCCESS: _default_paths returned: {paths}")
        
        # Check if directories exist
        for name, path in paths.items():
            exists = path.exists()
            print(f"  {name}: {path} (exists: {exists})")
            
    except Exception as e:
        print(f"ERROR in _default_paths: {e}")
        import traceback
        traceback.print_exc()

def test_ensure_dir():
    """Test the _ensure_dir function specifically"""
    print("\nTesting _ensure_dir function...")
    
    try:
        from caliper_v2.ui_dash.app import _ensure_dir
        
        # Test with a normal directory
        test_dir = Path("test_dir_temp")
        result = _ensure_dir(test_dir)
        print(f"SUCCESS: _ensure_dir created {result}")
        
        # Clean up
        if test_dir.exists():
            test_dir.rmdir()
            print("Cleaned up test directory")
            
        # Test with current directory (should not create)
        current_dir = Path(".")
        result2 = _ensure_dir(current_dir)
        print(f"SUCCESS: _ensure_dir handled current dir: {result2}")
        
    except Exception as e:
        print(f"ERROR in _ensure_dir: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Dash Tab Debug Test ===")
    test_ensure_dir()
    test_default_paths()
    test_dash_app_initialization()
    print("=== Test Complete ===")