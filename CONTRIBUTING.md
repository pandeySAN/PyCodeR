# Contributing to PyLint Pro

Thanks for your interest in contributing! This document provides guidelines for contributing to PyLint Pro.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/pylint-pro`
3. Install in development mode: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `python hooks/install-hook.py`

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
coverage run -m pytest tests/
coverage report

# Run specific test file
pytest tests/test_cache.py
```

### Adding New Detectors

1. Create detector module in `src/detectors/`
2. Implement detection logic using AST visitors
3. Add tests in `tests/test_detectors.py`
4. Update CLI to include new detector
5. Document in README

Example detector structure:

```python
import ast

class MyDetector(ast.NodeVisitor):
    def __init__(self, tree):
        self.issues = []
        self.visit(tree)
    
    def visit_FunctionDef(self, node):
        # Your detection logic
        self.generic_visit(node)
    
    def get_issues(self):
        return self.issues
```

### Code Style

- Follow PEP 8
- Use type hints where appropriate
- Keep functions focused (single responsibility)
- Avoid over-commenting (code should be self-explanatory)

### Testing Guidelines

- Write tests for new features
- Test edge cases
- Use descriptive test names
- Keep tests independent

## Areas for Contribution

### High Priority

- **Performance**: Parallel file analysis, faster CFG construction
- **Type Inference**: Better type tracking across functions
- **Security Patterns**: More vulnerability signatures
- **IDE Integration**: VSCode/PyCharm plugins

### Medium Priority

- **Configuration**: Support for `.pylintpro.json` config files
- **Auto-fix**: Expand automatic fix capabilities
- **Documentation**: More examples, tutorials
- **Cross-platform**: Better Windows support

### Good First Issues

- Add new security patterns
- Improve error messages
- Write documentation
- Add test coverage

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Update documentation if needed
6. Push to your fork
7. Open a pull request

### PR Guidelines

- Clear title and description
- Reference any related issues
- Include test coverage
- Keep PRs focused (one feature per PR)
- Update README if adding user-facing features

## Architecture Guidelines

### Key Principles

1. **Separation of Concerns**: Parser, CFG, Analysis, Detectors are separate
2. **No External Dependencies**: Keep runtime dependencies minimal (stdlib only)
3. **Performance First**: Cache aggressively, avoid redundant work
4. **Honest Limitations**: Document what the tool can't do

### Code Organization

```
src/
├── parser/      - AST parsing, symbol tables
├── cfg/         - Control flow graph
├── analysis/    - Dataflow algorithms
├── detectors/   - Issue detection
└── reporters/   - Output formatting
```

## Questions?

Open an issue or discussion on GitHub. We're happy to help!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
