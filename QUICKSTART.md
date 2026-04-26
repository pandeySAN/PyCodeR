# Quick Start Guide - PyLint Pro v2.0

Get started with PyLint Pro in under 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pylint-pro
cd pylint-pro

# Install
pip install -e .

# Verify installation
pylint-pro --help
```

## Your First Analysis

### 1. Analyze a Single File

```bash
pylint-pro examples/demo.py
```

**You'll see output like:**
```
======================================================================
File: examples/demo.py
======================================================================
[CRITICAL] Line 10: Hardcoded secret detected: API_KEY
[ERROR] Line 18: Calling 'upper' on potentially None object 'result'
[WARNING] Line 24: Unreachable code detected after return statement
[HIGH] Line 31: Infinite loop detected - no break or return inside loop
...

======================================================================
SUMMARY
======================================================================
Total files analyzed: 1
Total issues: 12
  Critical: 1
  Errors: 2
  High: 3
  Warnings: 5
  Info: 1
```

### 2. Analyze a Directory

```bash
# Analyze entire project
pylint-pro src/

# Analyze with caching (faster on subsequent runs)
pylint-pro src/
pylint-pro src/  # Much faster!
```

### 3. Generate Reports

```bash
# JSON report (for CI/CD)
pylint-pro src/ --format json --output report.json

# HTML report (shareable)
pylint-pro src/ --format html --output report.html
open report.html  # View in browser
```

## Common Use Cases

### CI/CD Integration

```bash
# In your CI pipeline
pylint-pro src/ --format json --output report.json

# Exit code is non-zero if critical/error issues found
if [ $? -ne 0 ]; then
    echo "Critical issues found!"
    exit 1
fi
```

### Focus on Specific Issues

```bash
# Only check security issues
pylint-pro src/ --enable security

# Skip complexity checks
pylint-pro src/ --disable complexity

# Multiple rules
pylint-pro src/ --enable security,dead_code,cross_file
```

### Performance Testing

```bash
# See analysis time
pylint-pro src/ --benchmark

# Clear cache and re-analyze
pylint-pro --clear-cache
pylint-pro src/ --benchmark
```

## Pre-commit Hook Setup

```bash
# Install git hook
python hooks/install-hook.py

# Now PyLint Pro runs on every commit
git commit -m "Your changes"
# → PyLint Pro automatically runs on staged files
```

## Understanding Output

### Severity Levels

- **CRITICAL**: Serious security issues, must fix immediately
- **ERROR**: Logic errors, type errors, will likely cause bugs
- **HIGH**: Potential issues, should investigate
- **WARNING**: Code quality issues, best practices
- **INFO**: Suggestions, style recommendations

### Issue Types

```
unused_import        - Imported but never used
dead_code           - Code that never executes
infinite_loop       - Loop with no exit condition
undefined_variable  - Variable used before definition
sql_injection       - SQL injection vulnerability
command_injection   - Command injection risk
hardcoded_secret    - Secrets in source code
type_error          - Type-related issues
complexity          - High cyclomatic complexity
```

## Next Steps

1. **Read the full README**: `README_NEW.md` for all features
2. **Check examples**: `examples/demo.py` shows various detections
3. **Run benchmarks**: `python benchmarks/run_benchmarks.py`
4. **Set up CI**: See `.github/workflows/pylint-pro.yml`

## Troubleshooting

### "No issues found" but I expect some

```bash
# Make sure you're analyzing the right files
pylint-pro src/ --benchmark  # Shows what's being analyzed

# Check if rules are disabled
pylint-pro src/  # No --disable flags
```

### Analysis is slow

```bash
# Use caching (enabled by default)
pylint-pro src/

# Second run should be much faster
# If not, clear and rebuild cache:
pylint-pro --clear-cache
```

### Too many false positives

```bash
# Disable specific rules
pylint-pro src/ --disable type_check,complexity

# Or only run high-value checks
pylint-pro src/ --enable security,dead_code
```

## Getting Help

- **Issues**: https://github.com/yourusername/pylint-pro/issues
- **Discussions**: https://github.com/yourusername/pylint-pro/discussions
- **Contributing**: See `CONTRIBUTING.md`

## What's Next?

Try these advanced features:

- Cross-file analysis: `--enable cross_file`
- Custom output files: `--output my-report.html`
- Rule combinations: `--enable security,cross_file --disable complexity`
- Benchmark your code: `--benchmark`

Happy analyzing! 🔍
