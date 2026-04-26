# PyLint Pro Usage Guide

## Quick Start

Analyze a Python file:

```bash
python -m src.cli yourfile.py
```

## Command Line Options

### Basic Analysis

```bash
python -m src.cli mycode.py
```

This runs all detectors and outputs to console.

### Output Formats

**JSON Output:**
```bash
python -m src.cli mycode.py -o json -f results.json
```

**HTML Report:**
```bash
python -m src.cli mycode.py -o html -f report.html
```

**Console (default):**
```bash
python -m src.cli mycode.py -o console
```

### CFG Visualization

Generate control flow graph in DOT format:

```bash
python -m src.cli mycode.py --cfg-dot
```

This creates `mycode.dot` which can be visualized with Graphviz:

```bash
dot -Tpng mycode.dot -o mycode.png
```

## Understanding Results

### Severity Levels

- **CRITICAL**: Security vulnerabilities requiring immediate attention
- **ERROR**: Logic bugs that will cause runtime failures
- **HIGH**: Serious issues that should be fixed
- **WARNING**: Code quality issues
- **INFO**: Suggestions for improvement

### Issue Types

**Logic Errors:**
- `undefined_variable`: Variable used before definition
- `unused_variable`: Variable defined but never used
- `code_after_terminator`: Unreachable code after return/raise
- `infinite_loop`: Loop without break condition

**Type Errors:**
- `none_type_error`: Calling method on potentially None object
- `arg_count_mismatch`: Function called with wrong number of arguments

**Security Issues:**
- `sql_injection`: String concatenation in SQL queries
- `hardcoded_password`: Hardcoded credentials
- `dangerous_function`: Use of eval/exec
- `command_injection`: Unsafe system command execution

**Code Quality:**
- `high_complexity`: Function exceeds complexity threshold
- `deep_nesting`: Excessive nesting depth
- `long_function`: Function exceeds recommended length

## Examples

### Example 1: Detect Unused Variables

**Code:**
```python
def calculate(x, y):
    result = x + y
    temp = x * y
    return result
```

**Output:**
```
WARNING (1 issues)
------------------------------------------------------------
  Line 3: Remove 'temp' or use it in your code
    Type: unused_variable
```

### Example 2: Detect None Type Errors

**Code:**
```python
def process(data):
    result = None
    if data:
        result = data.strip()
    return result.upper()
```

**Output:**
```
ERROR (1 issues)
------------------------------------------------------------
  Line 5: Calling 'upper' on potentially None object 'result'
    Type: none_type_error
```

### Example 3: Detect Security Issues

**Code:**
```python
password = "admin123"
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
```

**Output:**
```
CRITICAL (1 issues)
------------------------------------------------------------
  Line 3: Potential SQL injection - using string concatenation
    Type: sql_injection

HIGH (1 issues)
------------------------------------------------------------
  Line 1: Hardcoded secret detected
    Type: hardcoded_password
```

## Integration

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python -m src.cli $(git diff --cached --name-only --diff-filter=ACM | grep '.py$')
if [ $? -ne 0 ]; then
    echo "PyLint Pro found issues. Commit aborted."
    exit 1
fi
```

### CI/CD Integration

**GitHub Actions:**

```yaml
- name: Run PyLint Pro
  run: |
    python -m src.cli myapp/ -o json -f results.json
```

**Jenkins:**

```groovy
stage('Static Analysis') {
    steps {
        sh 'python -m src.cli src/ -o html -f analysis.html'
        publishHTML([reportDir: '.', reportFiles: 'analysis.html'])
    }
}
```

## Advanced Usage

### Analyzing Multiple Files

```bash
for file in src/*.py; do
    python -m src.cli "$file"
done
```

### Custom Thresholds

Edit `src/detectors/complexity.py` to adjust:
- `max_complexity`: Cyclomatic complexity threshold (default: 10)
- `max_nesting`: Maximum nesting depth (default: 4)
- `max_lines`: Maximum function length (default: 50)

## Interpreting CFG

The control flow graph shows all possible execution paths:

- **Nodes**: Basic blocks containing statements
- **Edges**: Possible control flow transitions
- **Entry**: Function/module entry point
- **Exit**: Function/module exit point

Branch nodes (if/while) have multiple outgoing edges representing different paths.

## Performance Tips

For large codebases:
- Analyze files in parallel
- Use JSON output and post-process
- Focus on critical severity issues first
- Run incrementally (only changed files)

## Troubleshooting

**"Failed to parse file"**
- Check Python syntax is valid
- Ensure file encoding is UTF-8

**"No issues found" but bugs exist**
- PyLint Pro focuses on specific bug patterns
- Some issues require runtime analysis
- Review analysis scope in documentation

**Slow analysis**
- Check file size (>50k lines may be slow)
- Profile with `--profile` flag
- Report performance issues on GitHub
