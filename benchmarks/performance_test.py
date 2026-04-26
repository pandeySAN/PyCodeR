import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cli import PyLintPro


def benchmark_file(filepath, iterations=3):
    times = []
    
    for i in range(iterations):
        start = time.time()
        
        analyzer = PyLintPro(filepath)
        issues = analyzer.analyze()
        
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    with open(filepath, 'r') as f:
        lines = len(f.readlines())
        
    print(f"\nBenchmark Results for {filepath}")
    print(f"Lines of code: {lines}")
    print(f"Average time: {avg_time:.4f}s")
    print(f"Min time: {min_time:.4f}s")
    print(f"Max time: {max_time:.4f}s")
    print(f"Issues found: {len(issues)}")
    print(f"Lines per second: {lines/avg_time:.0f}")
    
    return avg_time, issues


def generate_large_file(filepath, num_lines=10000):
    with open(filepath, 'w') as f:
        f.write("import os\nimport sys\n\n")
        
        for i in range(num_lines // 10):
            f.write(f"""
def function_{i}(x, y):
    result = x + y
    if result > 10:
        return result * 2
    else:
        return result
    
var_{i} = function_{i}({i}, {i+1})
""")
    
    print(f"Generated {filepath} with ~{num_lines} lines")
    return filepath


if __name__ == "__main__":
    test_file = "benchmark_test.py"
    
    generate_large_file(test_file, 10000)
    
    benchmark_file(test_file)
    
    os.remove(test_file)
