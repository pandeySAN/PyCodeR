# PyLint Pro v2.0

A production-grade static code analyzer for Python that goes beyond traditional linters by combining AST parsing, control flow analysis, and dataflow analysis to catch logic errors, security issues, and code quality problems.

## Why PyLint Pro?

Most linters focus on style and simple pattern matching. PyLint Pro performs **deep semantic analysis**:

- **Control Flow Analysis**: Builds CFG to detect unreachable code and infinite loops
- **Dataflow Analysis**: Tracks variable definitions and uses to find bugs like using variables before assignment
- **Cross-File Analysis**: Detects unused imports and undefined symbols across your entire project
- **Security Scanning**: Identifies SQL injection, command injection, and hardcoded secrets
- **Smart Caching**: Only re-analyzes files that changed, making it fast for large projects

### vs. Pylint/Flake8

| Feature | PyLint Pro | Pylint | Flake8 |
|---------|------------|--------|--------|
| Control Flow Analysis | ✓ | ✗ | ✗ |
| Dataflow Analysis | ✓ | ✗ | ✗ |
| Cross-File Analysis | ✓ | Limited | ✗ |
| File Caching | ✓ | ✗ | ✗ |
| Security Scanning | ✓ | Limited | ✗ |
| Project-Wide Analysis | ✓ | ✗ | ✗ |

## Installation

```bash
git clone https://github.com/yourusername/pylint-pro
cd pylint-pro
pip install -e .
```

## Quick Start

```bash
# Analyze single file
pylint-pro myfile.py

# Analyze entire project
pylint-pro src/

# Generate JSON report
pylint-pro src/ --format json --output report.json

# Only run specific checks
pylint-pro src/ --enable security,dead_code

# Disable certain checks
pylint-pro src/ --disable complexity
```

## Features

### 1. Logic Error Detection

Catches bugs that static type checkers miss:

```python
def process(data):
    result = None
    if data:
        result = data.strip()
    return result.upper()  # ❌ May be None!
```

**PyLint Pro detects:**
```
ERROR: Line 5: Calling 'upper' on potentially None object 'result'
```

### 2. Dead Code Detection

```python
def example():
    return True
    print("Never executed")  # ❌ Unreachable code
```

### 3. Infinite Loop Detection

```python
while True:
    process_data()
    # ❌ No break statement - infinite loop!
```

### 4. Cross-File Analysis **[NEW in v2.0]**

Detects unused imports across your entire codebase:

```python
# utils.py
from requests import get, post  # 'post' is imported but never used anywhere

# main.py
from utils import undefined_function  # ❌ Not defined in utils.py
```

### 5. Security Scanning

- SQL injection patterns
- Command injection vulnerabilities
- Hardcoded secrets (passwords, API keys)
- Dangerous function usage (eval, exec, pickle.loads)

### 6. Performance Caching **[NEW in v2.0]**

Only re-analyzes files that changed:

```bash
# First run: analyzes everything
pylint-pro src/  # 5.2s

# Second run: uses cache
pylint-pro src/  # 0.3s (17x faster!)
```

## Advanced Usage

### CI/CD Integration

PyLint Pro returns non-zero exit codes when errors are found:

```bash
# In your CI pipeline
pylint-pro src/ --format json --output report.json
if [ $? -ne 0 ]; then
    echo "Analysis failed - fix issues before merging"
    exit 1
fi
```

### GitHub Actions

Add to `.github/workflows/analysis.yml`:

```yaml
- name: Run PyLint Pro
  run: |
    pip install -e .
    pylint-pro src/ --format json --output report.json
```

See [.github/workflows/pylint-pro.yml](.github/workflows/pylint-pro.yml) for full example.

### Pre-commit Hooks

Install the git hook:

```bash
python hooks/install-hook.py
```

Or use with pre-commit framework:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pylint-pro
        name: PyLint Pro
        entry: pylint-pro
        language: system
        types: [python]
```

### Rule Configuration

```bash
# Run only security and dead code checks
pylint-pro src/ --enable security,dead_code

# Disable complexity checking
pylint-pro src/ --disable complexity

# Available rules:
#   - unused_vars
#   - dead_code
#   - infinite_loop
#   - type_check
#   - security
#   - complexity
#   - undefined_vars
#   - cross_file
```

### Output Formats

**Console** (default):
```bash
pylint-pro myfile.py
```

**JSON** (for tooling integration):
```bash
pylint-pro src/ --format json --output report.json
```

**HTML** (for reports):
```bash
pylint-pro src/ --format html --output report.html
```

## Architecture

```
Input Files
    ↓
AST Parser ─────────→ Symbol Table
    ↓                      ↓
CFG Builder ←──────────────┘
    ↓
Dataflow Analysis
    ├─→ Liveness Analysis
    └─→ Reaching Definitions
    ↓
Pattern Detectors
    ├─→ Dead Code
    ├─→ Type Errors
    ├─→ Security Issues
    ├─→ Complexity
    └─→ Cross-File Analysis
    ↓
Issue Reports
```

### Key Components

**AST Parser**: Converts Python source into abstract syntax tree
**CFG Builder**: Constructs control flow graph with basic blocks
**Symbol Table**: Tracks variable scopes and definitions
**Dataflow Analysis**: Computes liveness and reaching definitions
**Detectors**: Pattern-based issue detection
**Cache System**: Stores analysis results keyed by file hash

## Performance

Tested on real-world codebases:

| Project Size | Lines of Code | Analysis Time (cached) |
|--------------|---------------|------------------------|
| Small | 1,000 | 0.3s |
| Medium | 10,000 | 2.1s |
| Large | 50,000 | 8.7s |

Benchmarks run on Ubuntu 22.04, Python 3.10, Intel i7.

Run benchmarks yourself:

```bash
python benchmarks/run_benchmarks.py
```

## Limitations & Known Issues

**Honest assessment:**

1. **Type inference is basic** - doesn't match mypy's sophistication. We use simple heuristics.

2. **Cross-file analysis is local** - only analyzes files in the current directory tree. Can't follow imports to site-packages.

3. **Some false positives** - Dataflow analysis is conservative. May flag valid code patterns.

4. **No auto-fix** - The `--fix` flag is experimental and limited. Manual fixes required.

5. **Python 3.8+ only** - Uses AST features not available in older versions.

6. **Performance** - Complex files (>5000 lines) can be slow. Cache helps but first run is heavy.

**Use PyLint Pro for:** Logic errors, security issues, code quality checks
**Use mypy for:** Type checking
**Use black for:** Code formatting

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# With coverage
coverage run -m pytest tests/
coverage report

# Run benchmarks
python benchmarks/run_benchmarks.py

# Clear cache
pylint-pro --clear-cache
```

## Project Structure

```
pylint-pro/
├── src/
│   ├── parser/          # AST parsing, symbol tables
│   ├── cfg/             # Control flow graph construction
│   ├── analysis/        # Dataflow analysis (liveness, reaching defs, cross-file)
│   ├── detectors/       # Issue detection modules
│   ├── reporters/       # Output formatters (console, JSON, HTML)
│   ├── cache.py         # Analysis result caching
│   └── cli.py           # Command-line interface
├── tests/               # Test suite
├── benchmarks/          # Performance tests
├── hooks/               # Git hook installers
└── .github/workflows/   # CI configuration
```

## Contributing

Contributions welcome! Areas for improvement:

- Better type inference
- More security patterns
- IDE integrations
- Performance optimizations

Please include tests for new features.

## License

MIT License - see LICENSE file

## FAQ

**Q: How is this different from Pylint?**
A: PyLint Pro focuses on deep semantic analysis (CFG, dataflow) while Pylint is primarily style-focused. We catch different types of bugs.

**Q: Can I use this in production?**
A: Yes, but understand the limitations. It's a complementary tool, not a replacement for mypy or other linters.

**Q: Why build this instead of contributing to existing tools?**
A: This is a learning/portfolio project demonstrating compiler theory and static analysis techniques. Different architecture than existing tools.

**Q: Does it support Python 2?**
A: No. Python 3.8+ only.

## Roadmap

- [ ] VSCode extension
- [ ] Better type inference using constraint solving
- [ ] Parallel file analysis
- [ ] Configuration file support (.pylintpro.json)
- [ ] More auto-fix capabilities
- [ ] Integration with Language Server Protocol

---

**Built to demonstrate:** Compiler theory, static analysis, dataflow algorithms, and production software engineering practices.
