#!/usr/bin/env python3
"""
Performance benchmarking for PyLint Pro
Compares analysis time across different file sizes and scenarios
"""

import time
import tempfile
from pathlib import Path
import statistics
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli import PyLintPro


def generate_test_file(lines: int) -> str:
    """Generate a Python file with specified number of lines"""
    code_patterns = [
        "def function_{i}(x, y):\n    result = x + y\n    return result\n\n",
        "class Class_{i}:\n    def __init__(self):\n        self.value = {i}\n\n",
        "if True:\n    x = {i}\n    y = x * 2\n\n",
        "for i in range({i}):\n    print(i)\n\n",
    ]
    
    content = "# Auto-generated test file\n\n"
    pattern_idx = 0
    
    while len(content.split('\n')) < lines:
        content += code_patterns[pattern_idx].format(i=pattern_idx)
        pattern_idx = (pattern_idx + 1) % len(code_patterns)
    
    return content


def benchmark_file_size(sizes=[100, 500, 1000, 5000], runs=3):
    """Benchmark analysis time for different file sizes"""
    print("="*70)
    print("BENCHMARK: File Size vs Analysis Time")
    print("="*70)
    print(f"{'Lines':<10} {'Avg Time (s)':<15} {'Min (s)':<12} {'Max (s)':<12}")
    print("-"*70)
    
    results = {}
    
    for size in sizes:
        times = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(generate_test_file(size))
            filepath = f.name
        
        try:
            # Warm-up run
            analyzer = PyLintPro(filepath, use_cache=False)
            analyzer.analyze()
            
            # Timed runs
            for _ in range(runs):
                analyzer = PyLintPro(filepath, use_cache=False)
                start = time.time()
                analyzer.analyze()
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"{size:<10} {avg_time:<15.4f} {min_time:<12.4f} {max_time:<12.4f}")
            
            results[size] = {
                'avg': avg_time,
                'min': min_time,
                'max': max_time
            }
            
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    return results


def benchmark_cache_impact(file_size=1000, runs=5):
    """Benchmark cache performance"""
    print("\n" + "="*70)
    print("BENCHMARK: Cache Impact")
    print("="*70)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(generate_test_file(file_size))
        filepath = f.name
    
    try:
        # Without cache
        no_cache_times = []
        for _ in range(runs):
            analyzer = PyLintPro(filepath, use_cache=False)
            start = time.time()
            analyzer.analyze()
            no_cache_times.append(time.time() - start)
        
        # With cache (first run populates cache)
        analyzer = PyLintPro(filepath, use_cache=True)
        analyzer.analyze()
        
        cached_times = []
        for _ in range(runs):
            analyzer = PyLintPro(filepath, use_cache=True)
            start = time.time()
            analyzer.analyze()
            cached_times.append(time.time() - start)
        
        no_cache_avg = statistics.mean(no_cache_times)
        cached_avg = statistics.mean(cached_times)
        speedup = no_cache_avg / cached_avg if cached_avg > 0 else 0
        
        print(f"Without cache: {no_cache_avg:.4f}s (avg)")
        print(f"With cache:    {cached_avg:.4f}s (avg)")
        print(f"Speedup:       {speedup:.2f}x")
        
    finally:
        Path(filepath).unlink(missing_ok=True)
        # Clean cache
        from src.cache import AnalysisCache
        cache = AnalysisCache()
        cache.clear()


def benchmark_detectors(file_size=500):
    """Benchmark individual detector performance"""
    print("\n" + "="*70)
    print("BENCHMARK: Detector Performance")
    print("="*70)
    print(f"{'Detector':<25} {'Time (s)':<15}")
    print("-"*70)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(generate_test_file(file_size))
        filepath = f.name
    
    try:
        # Test each detector individually
        detectors = [
            'unused_vars',
            'dead_code',
            'type_check',
            'security',
            'complexity',
            'undefined_vars'
        ]
        
        for detector in detectors:
            analyzer = PyLintPro(filepath, use_cache=False, enabled_rules=[detector])
            start = time.time()
            analyzer.analyze()
            elapsed = time.time() - start
            print(f"{detector:<25} {elapsed:<15.4f}")
            
    finally:
        Path(filepath).unlink(missing_ok=True)


def main():
    print("\nPyLint Pro Performance Benchmark")
    print("="*70)
    
    benchmark_file_size()
    benchmark_cache_impact()
    benchmark_detectors()
    
    print("\n" + "="*70)
    print("Benchmark complete!")
    print("="*70)


if __name__ == '__main__':
    main()
