#!/usr/bin/env python3
"""
Performance benchmarking for PyLint Pro

Runs the analyzer on generated files and on real open-source repositories
(cloned shallowly into a temp folder), reporting:
  * files analysed
  * total time cold vs cached
  * issues per category
"""

import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli import PyLintPro

# Real open-source projects to benchmark against (shallow clones).
REAL_REPOS = [
    ("requests", "https://github.com/psf/requests.git"),
    ("flask", "https://github.com/pallets/flask.git"),
]


def generate_test_file(lines: int) -> str:
    """Generate a Python file with specified number of lines."""
    code_patterns = [
        "def function_{i}(x, y):\n    result = x + y\n    return result\n\n",
        "class Class_{i}:\n    def __init__(self):\n        self.value = {i}\n\n",
        "if True:\n    x = {i}\n    y = x * 2\n\n",
        "for i in range({i}):\n    print(i)\n\n",
    ]

    content = "# Auto-generated test file\n\n"
    pattern_idx = 0

    while len(content.split("\n")) < lines:
        content += code_patterns[pattern_idx].format(i=pattern_idx)
        pattern_idx = (pattern_idx + 1) % len(code_patterns)

    return content


def _clone_repo(repo_name, repo_url, target_dir):
    """Shallow-clone a repo into target_dir. Returns True on success."""
    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", repo_url, str(target_dir)],
            check=True,
            capture_output=True,
            timeout=300,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  (could not clone {repo_name}: {e})")
        return False


def _collect_python_files(root):
    """Return all .py files under root, skipping venv/build dirs."""
    skip = {"__pycache__", ".git", ".venv", "venv", "env", ".tox", "build", "dist", ".eggs"}
    files = []
    for path in Path(root).rglob("*.py"):
        if not any(part in skip for part in path.parts):
            files.append(str(path))
    return sorted(files)


def _categorize(issue):
    itype = issue.get("type", "unknown")
    if itype.startswith("unused_"):
        return "unused"
    if itype == "undefined_variable":
        return "undefined_variable"
    if itype in ("dead_code", "unreachable_block", "code_after_terminator"):
        return "dead_code"
    if itype == "infinite_loop":
        return "infinite_loop"
    if itype == "arg_count_mismatch":
        return "arg_count_mismatch"
    if itype == "none_type_error":
        return "none_type_error"
    if itype in ("sql_injection", "hardcoded_password", "hardcoded_api_key",
                 "hardcoded_secret", "hardcoded_token", "dangerous_function",
                 "command_injection", "pickle_loads"):
        return "security"
    if itype == "undefined_import":
        return "undefined_import"
    return "other"


def analyze_repo_files(filepaths, use_cache=True):
    """Analyze a list of files, return (total_time, issues_by_file, all_issues)."""
    start = time.time()
    all_issues = []
    issues_by_file = {}
    for filepath in filepaths:
        analyzer = PyLintPro(filepath, use_cache=use_cache)
        issues = analyzer.analyze()
        issues_by_file[filepath] = issues
        all_issues.extend(issues)
    elapsed = time.time() - start
    return elapsed, issues_by_file, all_issues


def benchmark_file_size(sizes=[100, 500, 1000, 5000], runs=3):
    """Benchmark analysis time for different file sizes."""
    print("=" * 70)
    print("BENCHMARK: File Size vs Analysis Time (generated files)")
    print("=" * 70)
    print(f"{'Lines':<10} {'Avg Time (s)':<15} {'Min (s)':<12} {'Max (s)':<12}")
    print("-" * 70)

    results = {}

    for size in sizes:
        times = []

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(generate_test_file(size))
            filepath = f.name

        try:
            # Warm-up run
            analyzer = PyLintPro(filepath, use_cache=False)
            analyzer.analyze()

            for _ in range(runs):
                analyzer = PyLintPro(filepath, use_cache=False)
                start = time.time()
                analyzer.analyze()
                times.append(time.time() - start)

            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)

            print(f"{size:<10} {avg_time:<15.4f} {min_time:<12.4f} {max_time:<12.4f}")
            results[size] = {"avg": avg_time, "min": min_time, "max": max_time}

        finally:
            Path(filepath).unlink(missing_ok=True)

    return results


def benchmark_cache_impact(file_size=1000, runs=5):
    """Benchmark cache performance on a generated file."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Cache Impact (generated file)")
    print("=" * 70)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(generate_test_file(file_size))
        filepath = f.name

    try:
        no_cache_times = []
        for _ in range(runs):
            analyzer = PyLintPro(filepath, use_cache=False)
            start = time.time()
            analyzer.analyze()
            no_cache_times.append(time.time() - start)

        # Populate cache
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

        print(f"Without cache: {no_cache_avg:.4f}s (avg over {runs} runs)")
        print(f"With cache:    {cached_avg:.4f}s (avg over {runs} runs)")
        print(f"Speedup:       {speedup:.2f}x")

    finally:
        Path(filepath).unlink(missing_ok=True)
        from src.cache import AnalysisCache
        AnalysisCache().clear()


def benchmark_real_repos():
    """Analyze real open-source repos; report files, cold vs cached time,
    and issues per category."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Real Open-Source Repositories")
    print("=" * 70)

    tmp_root = Path(tempfile.mkdtemp(prefix="pylint-pro-bench-"))
    try:
        for repo_name, repo_url in REAL_REPOS:
            print(f"\n--- {repo_name} ---")
            repo_dir = tmp_root / repo_name
            if not _clone_repo(repo_name, repo_url, repo_dir):
                continue

            files = _collect_python_files(repo_dir)
            print(f"Files analysed: {len(files)}")

            if not files:
                print("  (no Python files found)")
                continue

            # Cold run: no cache at all.
            cold_time, cold_by_file, cold_issues = analyze_repo_files(
                files, use_cache=False
            )

            # Populate the cache with a first pass (not timed).
            analyze_repo_files(files, use_cache=True)

            # Warm run: every file hits the cache.
            warm_time, warm_by_file, warm_issues = analyze_repo_files(
                files, use_cache=True
            )

            cold_categories = Counter(_categorize(i) for i in cold_issues)
            warm_categories = Counter(_categorize(i) for i in warm_issues)

            print(f"Cold time:   {cold_time:.3f}s  ({len(cold_issues)} issues)")
            print(f"Cached time: {warm_time:.3f}s  ({len(warm_issues)} issues)")
            speedup = cold_time / warm_time if warm_time > 0 else 0
            print(f"Speedup:     {speedup:.2f}x")
            print("Issues by category (cold):",
                  dict(sorted(cold_categories.items())))
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
        from src.cache import AnalysisCache
        AnalysisCache().clear()


def main():
    print("\nPyLint Pro Performance Benchmark")
    print("=" * 70)

    benchmark_file_size()
    benchmark_cache_impact()
    benchmark_real_repos()

    print("\n" + "=" * 70)
    print("Benchmark complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
