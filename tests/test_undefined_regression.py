import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cli import PyLintPro

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

REGRESSION_FIXTURES = [
    'clean_code.py',
    'regress_params.py',
    'regress_defaults.py',
    'regress_lambdas.py',
    'regress_comprehensions.py',
    'regress_try_except.py',
    'regress_with.py',
    'regress_global_nonlocal.py',
    'regress_decorators.py',
]


def _undefined_variable_issues(filepath):
    analyzer = PyLintPro(filepath, use_cache=False)
    issues = analyzer.analyze()
    return [i for i in issues if i.get('type') == 'undefined_variable']


class TestUndefinedVariableRegression(unittest.TestCase):
    """Regression tests: no false "used before definition" errors."""

    def test_clean_code_no_errors(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'clean_code.py'))
        self.assertEqual(issues, [], issues)

    def test_function_parameters_defined_at_entry(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_params.py'))
        self.assertEqual(issues, [], issues)

    def test_default_argument_values(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_defaults.py'))
        self.assertEqual(issues, [], issues)

    def test_lambda_parameters(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_lambdas.py'))
        self.assertEqual(issues, [], issues)

    def test_comprehension_variables(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_comprehensions.py'))
        self.assertEqual(issues, [], issues)

    def test_try_except_finally(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_try_except.py'))
        self.assertEqual(issues, [], issues)

    def test_with_target(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_with.py'))
        self.assertEqual(issues, [], issues)

    def test_global_and_nonlocal(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_global_nonlocal.py'))
        self.assertEqual(issues, [], issues)

    def test_decorators(self):
        issues = _undefined_variable_issues(
            os.path.join(FIXTURES_DIR, 'regress_decorators.py'))
        self.assertEqual(issues, [], issues)


if __name__ == '__main__':
    unittest.main()
