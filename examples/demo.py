"""
Example code with various issues that PyLint Pro can detect.
Run: pylint-pro examples/demo.py
"""

import os
import sys
import json  # Unused import - will be detected by cross-file analysis

# Hardcoded secret - security issue
API_KEY = "sk-1234567890abcdef"


def process_data(data):
    """Example with NoneType error"""
    result = None
    if data:
        result = data.strip()
    return result.upper()  # Potential NoneType error!


def unreachable_code_example():
    """Example with dead code"""
    return True
    print("This will never execute")  # Dead code


def infinite_loop_example():
    """Example with infinite loop"""
    counter = 0
    while counter < 10:
        print(counter)
        # Missing: counter += 1
        # This creates an infinite loop!


def sql_injection_example(user_input):
    """Example with SQL injection vulnerability"""
    import sqlite3
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    
    # Dangerous: string concatenation in SQL
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    cursor.execute(query)  # SQL injection risk!
    
    return cursor.fetchall()


def command_injection_example(filename):
    """Example with command injection"""
    import os
    
    # Dangerous: user input in system command
    command = "cat " + filename
    os.system(command)  # Command injection risk!


def complex_function(a, b, c, d, e):
    """Example with high cyclomatic complexity"""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return "too nested"  # Deep nesting detected
    return "ok"


def eval_usage(code):
    """Example with dangerous function"""
    return eval(code)  # Dangerous function usage!


def undefined_variable():
    """Example with variable used before definition"""
    if True:
        x = 10
    print(y)  # y is not defined


if __name__ == "__main__":
    # Examples that demonstrate various issues
    process_data(None)  # Will cause NoneType error
    
    # These would be caught in a real scenario
    # sql_injection_example("' OR '1'='1")
    # command_injection_example("; rm -rf /")
    # eval_usage("__import__('os').system('ls')")
