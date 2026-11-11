# Evaluation

## Methodology

PyLint Pro was run (cold cache, no cache) against two real open-source
repositories cloned shallowly into a temp folder:

| Repository | Version | Commit | Files analysed | Cold time | Cached time | Speedup |
|------------|---------|--------|----------------|-----------|-------------|---------|
| requests   | 2.34.2  | 3c7baaa0 | 37             | 17.80s    | 2.85s       | 6.25x   |
| flask      | 3.2.0.dev | 49943b5a | 83             | 16.27s    | 6.96s       | 2.34x   |

Times are end-to-end (parse + CFG + dataflow + all detectors), measured on
this machine with Python 3.13. Cached time re-uses results from the cold run
via the content-hash cache.

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

| Category | requests | flask |
|----------|----------|-------|
| undefined_variable | 1308 | 1305 |
| unused | 822 | 1503 |
| dead_code | 370 | 787 |
| arg_count_mismatch | 20 | 26 |
| security | 9 | 7 |
| other | 36 | 44 |
| **Total** | **2565** | **3672** |

"unused" combines unused_import, unused_function, unused_class, unused_variable.

## Manual false-positive review

A stratified random sample of **50 findings** across the real-repo output was
manually inspected against source context to classify each as a false positive
(FP) or true positive (TP).

| Category | Sample | FP | FP rate |
|----------|--------|----|---------|
| arg_count_mismatch | 6 | 6 | 100.0% |
| unused | 14 | 6 | 42.9% |
| undefined_variable | 14 | 1 | 7.1% |
| dead_code | 8 | 0 | 0.0% |
| security | 6 | 0 | 0.0% |
| other | 2 | 0 | 0.0% |
| **Overall** | **50** | **13** | **26.0%** |

Key observations:
- **arg_count_mismatch** is almost entirely FP on real code: external library
  functions (e.g. `urllib3.ProxyManager`, `werkzeug` CLI helpers) accept
  `*args`/`**kwargs`, which this analyzer does not model.
- **unused** is 42.9% FP because pytest test functions (`test_*`) and dunder
  methods (`__init__`, `__setstate__`) are referenced by frameworks, not by
  static source references.
- **undefined_variable** is mostly TP on real code; the single FP in the sample
  was a builtin name (`bytes`).
- **dead_code** and **security** findings had no FPs in the sample.

The detailed per-item review is recorded in `docs/evaluation_sample.md`.

## Known misses

- Type inference is limited to constants and a few builtin constructors; it
  does not catch most attribute/type errors beyond `None.upper()`-style cases.
- Cross-file analysis only resolves imports to files inside the scanned
  directory tree; imports from site-packages are not followed.
- `arg_count_mismatch` does not model `*args`/`**kwargs` or C-extension
  signatures, so it over-reports on wrapper functions.
- No dataflow tracking across function boundaries (inter-procedural analysis).
