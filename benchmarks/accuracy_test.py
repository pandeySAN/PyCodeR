import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cli import PyLintPro


test_cases = [
    {
        'name': 'Unused variable detection',
        'code': """
x = 5
y = 10
z = x
""",
        'expected_issues': ['unused_variable'],
        'expected_count': 1
    },
    {
        'name': 'Dead code after return',
        'code': """
def foo():
    return 5
    x = 10
""",
        'expected_issues': ['code_after_terminator'],
        'expected_count': 1
    },
    {
        'name': 'SQL injection',
        'code': """
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
""",
        'expected_issues': ['sql_injection'],
        'expected_count': 1
    },
    {
        'name': 'None type error',
        'code': """
x = None
y = x.upper()
""",
        'expected_issues': ['none_type_error'],
        'expected_count': 1
    },
    {
        'name': 'Infinite loop',
        'code': """
while True:
    x = 5
""",
        'expected_issues': ['infinite_loop'],
        'expected_count': 1
    }
]


def run_accuracy_tests():
    passed = 0
    failed = 0
    
    print("Running Accuracy Tests\n")
    print("=" * 60)
    
    for i, test in enumerate(test_cases):
        temp_file = f"test_case_{i}.py"
        
        with open(temp_file, 'w') as f:
            f.write(test['code'])
            
        try:
            analyzer = PyLintPro(temp_file)
            issues = analyzer.analyze()
            
            issue_types = [issue.get('type') for issue in issues]
            
            found_expected = any(exp in issue_types for exp in test['expected_issues'])
            
            if found_expected:
                print(f"✓ PASS: {test['name']}")
                passed += 1
            else:
                print(f"✗ FAIL: {test['name']}")
                print(f"  Expected: {test['expected_issues']}")
                print(f"  Found: {issue_types}")
                failed += 1
                
        except Exception as e:
            print(f"✗ ERROR: {test['name']}")
            print(f"  {str(e)}")
            failed += 1
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
    print("=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")
    print(f"Accuracy: {passed/(passed+failed)*100:.1f}%")
    
    return passed, failed


if __name__ == "__main__":
    run_accuracy_tests()
