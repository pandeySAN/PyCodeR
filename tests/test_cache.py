import pytest
import tempfile
import time
from pathlib import Path
from src.cache import AnalysisCache


def test_cache_initialization():
    """Test cache directory creation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = AnalysisCache(cache_dir=f"{tmpdir}/.cache")
        assert cache.cache_dir.exists()


def test_cache_get_set():
    """Test basic cache operations"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = AnalysisCache(cache_dir=f"{tmpdir}/.cache")
        
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("x = 1")
        
        # Set cache
        test_data = [{'type': 'test', 'line': 1}]
        cache.set(str(test_file), test_data)
        
        # Get cache
        cached = cache.get(str(test_file))
        assert cached == test_data


def test_cache_invalidation():
    """Test that cache invalidates when file changes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = AnalysisCache(cache_dir=f"{tmpdir}/.cache")
        
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("x = 1")
        
        # Cache data
        cache.set(str(test_file), ['data1'])
        assert cache.is_cached(str(test_file))
        
        # Modify file
        time.sleep(0.01)  # Ensure mtime changes
        test_file.write_text("x = 2")
        
        # Cache should be invalid
        assert not cache.is_cached(str(test_file))


def test_cache_clear():
    """Test clearing cache"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = AnalysisCache(cache_dir=f"{tmpdir}/.cache")
        
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("x = 1")
        
        cache.set(str(test_file), ['data'])
        assert cache.is_cached(str(test_file))
        
        cache.clear()
        assert not cache.is_cached(str(test_file))


def test_cache_missing_file():
    """Test behavior with missing file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = AnalysisCache(cache_dir=f"{tmpdir}/.cache")
        
        result = cache.get("/nonexistent/file.py")
        assert result is None
