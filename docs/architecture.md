# PyLint Pro Architecture

## Overview

PyLint Pro is a static code analyzer built on compiler theory principles. It analyzes Python code without executing it to find bugs, security issues, and code quality problems.

## Architecture Layers

### 1. Parser Layer

**Components:**
- `ast_parser.py`: Converts source code to Abstract Syntax Tree
- `symbol_table.py`: Tracks all variables, functions, classes with scope information

**Responsibilities:**
- Parse Python source code into AST
- Build symbol table with scope tracking
- Handle imports, functions, classes, variables

### 2. Control Flow Graph Layer

**Components:**
- `basic_block.py`: Represents code blocks
- `cfg_builder.py`: Constructs control flow graph

**Responsibilities:**
- Create CFG from AST
- Handle if/else, loops, try/except
- Track all possible execution paths

### 3. Analysis Layer

**Components:**
- `dataflow.py`: Core data flow analysis framework
- `liveness.py`: Liveness analysis (backward)
- `reaching_defs.py`: Reaching definitions (forward)

**Responsibilities:**
- Track variable lifetime
- Find def-use chains
- Detect uninitialized variables

### 4. Detection Layer

**Components:**
- `unused_vars.py`: Unused code detection
- `dead_code.py`: Unreachable code detection
- `type_checker.py`: Type inference and checking
- `security.py`: Security vulnerability scanning
- `complexity.py`: Code complexity metrics

**Responsibilities:**
- Apply pattern matching on AST/CFG
- Run data flow analysis results
- Classify issues by severity

### 5. Reporting Layer

**Components:**
- `console.py`: Terminal output
- `json_reporter.py`: JSON format
- `html_reporter.py`: HTML dashboard

**Responsibilities:**
- Format analysis results
- Group by severity
- Generate human-readable reports

## Data Flow

```
Source Code
    ↓
AST Parser (Python ast module)
    ↓
Symbol Table (scope tracking)
    ↓
CFG Builder (basic blocks + edges)
    ↓
Data Flow Analysis (liveness + reaching defs)
    ↓
Detectors (pattern matching)
    ↓
Reporters (output formatting)
```

## Key Algorithms

### Liveness Analysis

Backward dataflow analysis to determine which variables are "alive" at each program point.

**Algorithm:**
1. Initialize all variables as dead
2. Walk backward through CFG from exit
3. When variable is used, mark as live
4. When variable is defined, kill previous liveness
5. Iterate until fixed point

**Use:** Detect unused variables

### Reaching Definitions

Forward dataflow analysis to track which assignments reach each program point.

**Algorithm:**
1. For each assignment, create definition
2. Walk forward through CFG from entry
3. Track which definitions reach each block
4. New assignment kills previous definitions
5. Iterate until fixed point

**Use:** Detect use-before-definition

### Cyclomatic Complexity

Measures code complexity based on decision points.

**Formula:** CC = E - N + 2P
- E = edges in CFG
- N = nodes in CFG  
- P = connected components

**Use:** Identify overly complex functions

## Design Decisions

### Why AST over Regex?

AST provides structure-aware parsing that understands Python syntax, while regex is brittle and error-prone for code analysis.

### Why CFG?

CFG enables path-sensitive analysis and tracks all possible execution flows, catching bugs that simple AST walking misses.

### Why Data Flow Analysis?

Tracks how values flow through the program, enabling detection of use-before-definition, unused variables, and type errors.

### Why Fixed-Point Iteration?

Some analyses (liveness, reaching defs) require iterating until results converge. Fixed-point ensures correctness.

## Extensibility

### Adding New Detectors

1. Create detector class in `src/detectors/`
2. Implement detection logic using AST/CFG/analysis results
3. Return issues in standard format
4. Add to CLI pipeline

### Adding New Reports

1. Create reporter class in `src/reporters/`
2. Implement `report()` method
3. Add format option to CLI

## Performance Considerations

- AST parsing is fast (native Python)
- CFG construction is O(n) where n = statements
- Data flow analysis is O(n*k) where k = iterations
- Most analyses complete in <100ms for typical files

## Testing Strategy

- Unit tests for each component
- Integration tests for end-to-end flow
- Accuracy tests against known bugs
- Performance benchmarks on large files
