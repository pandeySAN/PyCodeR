import pytest
import tempfile
from pathlib import Path
from src.analysis.cross_file import analyze_cross_file, CrossFileAnalyzer


def test_unused_import_detection():
    """Test detection of unused imports"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file with unused import
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
import os
import sys

def main():
    print("Hello")
""")
        
        issues = analyze_cross_file([str(test_file)])
        
        # Should detect unused os and sys imports
        unused = [i for i in issues if i['type'] == 'unused_import']
        assert len(unused) >= 1


def test_used_import_not_flagged():
    """Test that used imports are not flagged"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
import os

def main():
    return os.path.exists('.')
""")
        
        issues = analyze_cross_file([str(test_file)])
        unused = [i for i in issues if i['type'] == 'unused_import' and 'os' in i['message']]
        
        # os is used, should not be flagged
        assert len(unused) == 0


def test_cross_file_undefined_import():
    """Test detection of undefined imports from local modules"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create module with defined function
        module_file = Path(tmpdir) / "mymodule.py"
        module_file.write_text("""
def existing_function():
    pass
""")
        
        # Create file importing undefined function
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
from mymodule import existing_function, undefined_function

existing_function()
""")
        
        issues = analyze_cross_file([str(test_file), str(module_file)])
        
        # Should detect undefined import
        undefined = [i for i in issues if i['type'] == 'undefined_import']
        assert len(undefined) >= 1


def test_multiple_files():
    """Test analysis across multiple files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.py"
        file1.write_text("import json\nimport sys")
        
        file2 = Path(tmpdir) / "file2.py"
        file2.write_text("import os\nimport re")
        
        issues = analyze_cross_file([str(file1), str(file2)])
        
        # Should find unused imports in both files
        assert len(issues) >= 2


def test_star_import():
    """Test handling of star imports"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("from os import *")
        
        # Should not crash on star imports
        issues = analyze_cross_file([str(test_file)])
        assert isinstance(issues, list)
