# Evaluation

## Methodology

PyLint Pro was run (cold cache, no cache) against two real open-source
repositories cloned shallowly into a temp folder:

| Repository | Version | Commit | Files analysed | Cold time | Cached time | Speedup |
|------------|---------|--------|----------------|-----------|-------------|---------|
| requests   | 2.34.2  | 3c7baaa | 37             | 9.84s     | 1.12s       | 8.78x   |
| flask      | 3.2.0.dev | 49943b5 | 83             | 7.83s     | 2.73s       | 2.87x   |

Times are end-to-end (parse + CFG + dataflow + all detectors), measured on
this machine with Python 3.13. Cached time re-uses results from the cold run
via the content-hash JSON cache.

## Benchmark results (generated files)

| Lines | Avg time (s) | Min (s) | Max (s) |
|-------|--------------|---------|---------|
| 100   | 0.017        | 0.015   | 0.019   |
| 500   | 0.129        | 0.121   | 0.137   |
| 1000  | 0.313        | 0.254   | 0.355   |
| 5000  | 12.16        | 10.86   | 13.53   |

Cache impact on a 1000-line generated file (5 runs):
- Without cache: 0.508s avg
- With cache: 0.035s avg
- Speedup: 14.40x

## Issues per category (cold run, real repos)

| Category | requests | flask | Total |
|----------|----------|-------|-------|
| undefined_variable | 2210 | 1882 | 4092 |
| unused | 392 | 1037 | 1429 |
| dead_code | 370 | 787 | 1157 |
| complexity | 36 | 44 | 80 |
| arg_count_mismatch | 16 | 24 | 40 |
| security | 9 | 7 | 16 |
| **Total** | **3033** | **3781** | **6814** |

"unused" combines unused_import, unused_function, unused_class, unused_variable.
"complexity" combines long_function, high_complexity, deep_nesting.
"dead_code" combines unreachable_block, code_after_terminator.
"security" combines dangerous_function, sql_injection, hardcoded_password,
hardcoded_secret, pickle_loads, etc.

## Manual false-positive review

A stratified random sample of **116 findings** (20 per category where available;
all 16 security findings since fewer than 20 exist) across the real-repo output
was manually inspected against source context to classify each as a false
positive (FP) or true positive (TP).

| Category | Sample | FP | FP rate |
|----------|--------|----|---------|
| arg_count_mismatch | 20 | 19 | 95.0% |
| complexity | 20 | 0 | 0.0% |
| dead_code | 20 | 20 | 100.0% |
| security | 16 | 0 | 0.0% |
| undefined_variable | 20 | 17 | 85.0% |
| unused | 20 | 11 | 55.0% |
| **Overall** | **116** | **67** | **57.8%** |

Key observations:

- **arg_count_mismatch (95% FP):** Almost entirely false positives because the
  analyzer does not model default argument values or keyword arguments. A call
  like `f(a, b, c=1)` where `f(a, b, c=2)` is defined is flagged because the
  analyzer counts only positional arguments (`len(node.args)`), missing the
  keyword argument and the default value. The single TP was a method call
  genuinely missing required arguments (`invoke` missing `app` and `runner`).

- **dead_code (100% FP):** All 20 sampled findings are function entry blocks
  flagged as unreachable. These are functions called dynamically by frameworks
  (Flask route handlers, pytest test functions, Werkzeug converters, error
  handlers) that the single-file static analysis cannot see being invoked.

- **undefined_variable (85% FP):** Mostly false positives from imported module
  names (`flask`, `requests`, `pytest`, `time`), `except X as e` names, module-
  level names used inside functions, and the walrus operator. The 3 TPs were
  genuine possible-undefined cases: a variable defined later in the same
  function (`line` defined after use), a variable conditionally defined inside
  an `if` block and used outside (`server_url`), and a name only imported under
  `TYPE_CHECKING` (`_AppCtxGlobals`).

- **unused (55% FP):** False positives are mostly functions invoked by
  frameworks (Flask route handlers, test functions, pytest fixtures, error
  handlers, View methods, converter methods) and imports used only in type
  annotations (`from __future__ import annotations`, `TypeVar`). True positives
  are genuinely unused class attributes, methods, and imports.

- **complexity (0% FP):** All findings are accurate complexity/length
  measurements. Long functions and deep nesting are real code properties,
  though whether they constitute "bugs" is subjective.

- **security (0% FP):** All findings are genuine security concerns:
  `pickle.loads()`, `exec()`, `eval()`, `__import__()`, and hardcoded
  passwords. Even in test code, these are real security patterns.

## Known misses

- Type inference is limited to constants and a few builtin constructors; it
  does not catch most attribute/type errors beyond `None.upper()`-style cases.
- Cross-file analysis only resolves imports to files inside the scanned
  directory tree; imports from site-packages are not followed.
- `arg_count_mismatch` does not model default values, `*args`/`**kwargs`, or
  keyword arguments, so it over-reports on functions with optional parameters.
- Dead-code analysis cannot see dynamic calls from frameworks (Flask routing,
  pytest, Werkzeug), so it flags all framework-invoked function entry points.
- No dataflow tracking across function boundaries (inter-procedural analysis).
- `unused` analysis cannot see external calls to public APIs (methods on
  classes meant for subclassing, signal handlers, etc.).

## Detailed per-item review

The detailed per-item review is recorded in `docs/review_sample_v2.txt`, with
machine-readable records in `docs/review_sample_v2.jsonl`.
