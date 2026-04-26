import hashlib
import json
import pickle
import os
from pathlib import Path
from typing import Dict, Optional, Any


class AnalysisCache:
    """
    Cache analysis results to avoid re-analyzing unchanged files.
    Uses file content hash as cache key.
    """
    
    def __init__(self, cache_dir: str = ".pylint-pro-cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
            
    def _compute_hash(self, filepath: str) -> str:
        """Compute SHA256 hash of file content"""
        with open(filepath, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
            
    def get_cache_path(self, filepath: str) -> Path:
        """Get cache file path for a given source file"""
        file_hash = self._compute_hash(filepath)
        cache_path = self.cache_dir / f"{file_hash}.pkl"
        return cache_path
        
    def is_cached(self, filepath: str) -> bool:
        """Check if analysis results are cached for this file"""
        try:
            file_hash = self._compute_hash(filepath)
            cache_file = self.cache_dir / f"{file_hash}.pkl"
            
            if not cache_file.exists():
                return False
                
            # Also check if file hasn't been modified
            cached_mtime = self.metadata.get(filepath, {}).get('mtime', 0)
            current_mtime = Path(filepath).stat().st_mtime
            
            return cached_mtime == current_mtime
        except:
            return False
            
    def get(self, filepath: str) -> Optional[Any]:
        """Retrieve cached analysis results"""
        if not self.is_cached(filepath):
            return None
            
        try:
            cache_path = self.get_cache_path(filepath)
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                return data
        except Exception as e:
            # Cache corruption, ignore
            return None
            
    def set(self, filepath: str, data: Any):
        """Store analysis results in cache"""
        try:
            cache_path = self.get_cache_path(filepath)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
                
            # Update metadata
            self.metadata[filepath] = {
                'mtime': Path(filepath).stat().st_mtime,
                'hash': self._compute_hash(filepath)
            }
            self._save_metadata()
        except Exception as e:
            # Silently fail if caching doesn't work
            pass
            
    def clear(self):
        """Clear entire cache"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata = {}
        self._save_metadata()
