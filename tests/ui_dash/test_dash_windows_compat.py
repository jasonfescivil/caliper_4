"""Test Windows-specific functionality."""
import pytest


@pytest.mark.windows
@pytest.mark.unit
class TestWindowsCompatibility:
    """Test Windows-specific features."""
    
    def test_path_cleaning_quoted(self):
        """Test path cleaning handles quoted Windows paths."""
        from caliper_v2.ui_dash.app import _clean_path_str
        
        # Test quoted path
        result = _clean_path_str('"C:\\test\\path"')
        assert result == "C:\\test\\path"
        
        # Test single quoted path
        result2 = _clean_path_str("'C:\\test\\path'")
        assert result2 == "C:\\test\\path"
    
    def test_path_cleaning_unquoted(self):
        """Test path cleaning preserves unquoted paths."""
        from caliper_v2.ui_dash.app import _clean_path_str
        
        result = _clean_path_str("C:\\test\\path")
        assert result == "C:\\test\\path"
    
    def test_path_cleaning_with_spaces(self):
        """Test path cleaning handles paths with spaces."""
        from caliper_v2.ui_dash.app import _clean_path_str
        
        result = _clean_path_str("C:\\Program Files\\test")
        assert result == "C:\\Program Files\\test"
        
        result2 = _clean_path_str('"C:\\Program Files\\test"')
        assert result2 == "C:\\Program Files\\test"
    
    def test_path_cleaning_empty(self):
        """Test path cleaning handles empty input."""
        from caliper_v2.ui_dash.app import _clean_path_str
        
        assert _clean_path_str("") == ""
        assert _clean_path_str(None) == ""
    
    def test_preview_nodes_function(self):
        """Test _preview_nodes function extracts data correctly."""
        from caliper_v2.ui_dash.app import _preview_nodes
        
        test_data = {
            "retrieval": {
                "nodes": [
                    {
                        "text": "Test text",
                        "score": 0.95,
                        "metadata": {
                            "file_name": "test.pdf",
                            "page": 1,
                            "section": "Introduction"
                        }
                    }
                ]
            }
        }
        
        rows = _preview_nodes(test_data)
        assert len(rows) == 1
        assert rows[0]["file"] == "test.pdf"
        assert rows[0]["page"] == 1
        assert rows[0]["section"] == "Introduction"
        assert rows[0]["score"] == 0.95
