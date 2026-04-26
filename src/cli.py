import sys
import argparse
from pathlib import Path
from typing import List, Dict
import time

from .parser.ast_parser import ASTParser
from .parser.symbol_table import build_symbol_table
from .cfg.cfg_builder import build_cfg
from .analysis.dataflow import analyze_dataflow
from .analysis.liveness import analyze_liveness
from .analysis.reaching_defs import ReachingDefinitions
from .analysis.cross_file import analyze_cross_file
from .detectors.unused_vars import detect_unused_vars
from .detectors.dead_code import detect_dead_code, InfiniteLoopDetector
from .detectors.type_checker import check_types
from .detectors.security import scan_security
from .detectors.complexity import analyze_complexity
from .fixes.suggestions import generate_suggestions
from .reporters.console import report_console
from .reporters.json_reporter import report_json
from .reporters.html_reporter import report_html
from .cache import AnalysisCache


class PyLintPro:
    def __init__(self, filepath, use_cache=True, enabled_rules=None, disabled_rules=None):
        self.filepath = filepath
        self.source_code = None
        self.tree = None
        self.symbol_table = None
        self.cfg = None
        self.all_issues = []
        self.use_cache = use_cache
        self.cache = AnalysisCache() if use_cache else None
        self.enabled_rules = enabled_rules or []
        self.disabled_rules = disabled_rules or []
        
    def analyze(self):
        # Try cache first
        if self.cache and self.cache.is_cached(self.filepath):
            cached_result = self.cache.get(self.filepath)
            if cached_result:
                self.all_issues = cached_result
                return self.all_issues
        
        self.load_file()
        self.parse()
        self.build_symbol_table()
        self.build_cfg()
        self.run_detectors()
        
        # Cache results
        if self.cache:
            self.cache.set(self.filepath, self.all_issues)
        
        return self.all_issues
        
    def load_file(self):
        try:
            with open(self.filepath, 'r') as f:
                self.source_code = f.read()
        except IOError as e:
            print(f"Error reading file {self.filepath}: {e}")
            sys.exit(1)
            
    def parse(self):
        parser = ASTParser(self.source_code)
        self.tree = parser.parse()
        
        if not self.tree:
            print("Failed to parse file")
            sys.exit(1)
            
    def build_symbol_table(self):
        self.symbol_table = build_symbol_table(self.tree)
        
    def build_cfg(self):
        self.cfg = build_cfg(self.tree)
        
    def run_detectors(self):
        # Filter detectors based on enabled/disabled rules
        if self._should_run_rule('unused_vars'):
            unused = detect_unused_vars(self.symbol_table, self.cfg)
            self.all_issues.extend(unused)
        
        if self._should_run_rule('dead_code'):
            dead = detect_dead_code(self.cfg, self.tree)
            self.all_issues.extend(dead)
        
        if self._should_run_rule('infinite_loop'):
            infinite_loop = InfiniteLoopDetector(self.tree)
            loops = infinite_loop.detect()
            self.all_issues.extend(loops)
        
        if self._should_run_rule('type_check'):
            type_issues = check_types(self.tree)
            self.all_issues.extend(type_issues)
        
        if self._should_run_rule('security'):
            security_issues = scan_security(self.tree, self.source_code)
            self.all_issues.extend(security_issues)
        
        if self._should_run_rule('complexity'):
            complexity_issues = analyze_complexity(self.tree)
            self.all_issues.extend(complexity_issues)
        
        if self._should_run_rule('undefined_vars'):
            reaching = ReachingDefinitions(self.cfg)
            reaching.analyze()
            undefined = reaching.find_undefined_uses()
            
            for undef in undefined:
                self.all_issues.append({
                    'type': 'undefined_variable',
                    'lineno': undef['lineno'],
                    'message': f"Variable '{undef['var']}' may be used before definition",
                    'severity': 'error'
                })
                
    def _should_run_rule(self, rule_name: str) -> bool:
        """Check if a rule should be executed based on config"""
        if self.disabled_rules and rule_name in self.disabled_rules:
            return False
        if self.enabled_rules and rule_name not in self.enabled_rules:
            return False
        return True


class ProjectAnalyzer:
    """Analyzer for entire projects/directories"""
    
    def __init__(self, path: str, use_cache=True, enabled_rules=None, disabled_rules=None):
        self.path = Path(path)
        self.use_cache = use_cache
        self.enabled_rules = enabled_rules
        self.disabled_rules = disabled_rules
        
    def find_python_files(self) -> List[str]:
        """Recursively find all Python files"""
        if self.path.is_file():
            return [str(self.path)]
            
        files = []
        for pattern in ['**/*.py']:
            files.extend([str(f) for f in self.path.glob(pattern) 
                         if not self._should_skip(f)])
        return files
        
    def _should_skip(self, filepath: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '__pycache__', '.git', '.venv', 'venv', 
            'env', '.tox', 'build', 'dist', '.eggs'
        ]
        return any(pattern in str(filepath) for pattern in skip_patterns)
        
    def analyze_all(self) -> Dict[str, List]:
        """Analyze all files in the project"""
        files = self.find_python_files()
        
        if not files:
            print(f"No Python files found in {self.path}")
            return {}
            
        results = {}
        
        print(f"Analyzing {len(files)} files...")
        
        for filepath in files:
            analyzer = PyLintPro(filepath, self.use_cache, 
                               self.enabled_rules, self.disabled_rules)
            try:
                issues = analyzer.analyze()
                results[filepath] = issues
            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")
                results[filepath] = []
                
        # Run cross-file analysis if enabled
        if self._should_run_rule('cross_file'):
            cross_issues = analyze_cross_file(files)
            for issue in cross_issues:
                file = issue.pop('file')
                if file in results:
                    results[file].append(issue)
                    
        return results
        
    def _should_run_rule(self, rule_name: str) -> bool:
        """Check if rule should run"""
        if self.disabled_rules and rule_name in self.disabled_rules:
            return False
        if self.enabled_rules and rule_name not in self.enabled_rules:
            return False
        return True


def main():
    parser = argparse.ArgumentParser(
        description='PyLint Pro - Advanced Static Code Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single file
  pylint-pro myfile.py
  
  # Analyze entire directory
  pylint-pro src/ --format json
  
  # Disable specific rules
  pylint-pro myfile.py --disable complexity,security
  
  # Only run specific rules
  pylint-pro myfile.py --enable unused_vars,dead_code
  
  # Clear cache and re-analyze
  pylint-pro myfile.py --no-cache
        """
    )
    
    parser.add_argument('path', nargs='?', help='Python file or directory to analyze')
    parser.add_argument('--format', '-f', 
                       choices=['console', 'json', 'html'],
                       default='console',
                       help='Output format (default: console)')
    parser.add_argument('--output', '-o', 
                       help='Output file for json/html reports')
    parser.add_argument('--cfg-dot', 
                       action='store_true',
                       help='Generate CFG in DOT format')
    parser.add_argument('--no-cache',
                       action='store_true',
                       help='Disable caching (re-analyze all files)')
    parser.add_argument('--enable',
                       help='Comma-separated list of rules to enable')
    parser.add_argument('--disable',
                       help='Comma-separated list of rules to disable')
    parser.add_argument('--fix',
                       action='store_true',
                       help='Attempt to auto-fix issues (experimental)')
    parser.add_argument('--benchmark',
                       action='store_true',
                       help='Show performance metrics')
    parser.add_argument('--clear-cache',
                       action='store_true',
                       help='Clear analysis cache and exit')
    
    args = parser.parse_args()
    
    # Handle cache clearing
    if args.clear_cache:
        cache = AnalysisCache()
        cache.clear()
        print("Cache cleared successfully")
        sys.exit(0)
    
    # Require path for analysis operations
    if not args.path:
        parser.error("the following arguments are required: path")
    
    # Parse enabled/disabled rules
    enabled_rules = args.enable.split(',') if args.enable else None
    disabled_rules = args.disable.split(',') if args.disable else None
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path {args.path} not found")
        sys.exit(1)
    
    start_time = time.time()
    use_cache = not args.no_cache
    
    # Determine if analyzing file or directory
    if path.is_file():
        analyzer = PyLintPro(str(path), use_cache, enabled_rules, disabled_rules)
        issues = analyzer.analyze()
        all_results = {str(path): issues}
        
        if args.cfg_dot and analyzer.cfg:
            dot_output = analyzer.cfg.to_dot()
            dot_file = str(path).replace('.py', '.dot')
            with open(dot_file, 'w') as f:
                f.write(dot_output)
            print(f"CFG saved to {dot_file}")
    else:
        # Directory analysis
        project_analyzer = ProjectAnalyzer(str(path), use_cache, 
                                          enabled_rules, disabled_rules)
        all_results = project_analyzer.analyze_all()
    
    elapsed_time = time.time() - start_time
    
    # Generate reports
    if args.format == 'console':
        _report_console_multi(all_results, args.benchmark, elapsed_time)
    elif args.format == 'json':
        output_file = args.output or 'pylint-pro-report.json'
        _report_json_multi(all_results, output_file)
        print(f"JSON report saved to {output_file}")
    elif args.format == 'html':
        output_file = args.output or 'pylint-pro-report.html'
        _report_html_multi(all_results, output_file)
        print(f"HTML report saved to {output_file}")
    
    # Calculate exit code
    has_errors = any(
        any(i.get('severity') in ['critical', 'error'] for i in issues)
        for issues in all_results.values()
    )
    
    exit_code = 1 if has_errors else 0
    sys.exit(exit_code)


def _report_console_multi(results: Dict[str, List], show_benchmark: bool, elapsed: float):
    """Report results for multiple files to console"""
    total_issues = sum(len(issues) for issues in results.values())
    
    if not total_issues:
        print("\n✓ No issues found")
        if show_benchmark:
            print(f"\nAnalysis completed in {elapsed:.2f}s")
        return
    
    # Group by severity
    by_severity = {'critical': 0, 'error': 0, 'high': 0, 'warning': 0, 'info': 0}
    
    for filepath, issues in results.items():
        if issues:
            print(f"\n{'='*70}")
            print(f"File: {filepath}")
            print('='*70)
            report_console(issues, filepath)
            
            for issue in issues:
                severity = issue.get('severity', 'info')
                by_severity[severity] = by_severity.get(severity, 0) + 1
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    print(f"Total files analyzed: {len(results)}")
    print(f"Total issues: {total_issues}")
    print(f"  Critical: {by_severity.get('critical', 0)}")
    print(f"  Errors: {by_severity.get('error', 0)}")
    print(f"  High: {by_severity.get('high', 0)}")
    print(f"  Warnings: {by_severity.get('warning', 0)}")
    print(f"  Info: {by_severity.get('info', 0)}")
    
    if show_benchmark:
        print(f"\nAnalysis completed in {elapsed:.2f}s")


def _report_json_multi(results: Dict[str, List], output_file: str):
    """Report results for multiple files to JSON"""
    import json
    
    # Aggregate statistics
    total_issues = sum(len(issues) for issues in results.values())
    by_severity = {'critical': 0, 'error': 0, 'high': 0, 'warning': 0, 'info': 0}
    
    for issues in results.values():
        for issue in issues:
            severity = issue.get('severity', 'info')
            by_severity[severity] = by_severity.get(severity, 0) + 1
    
    report = {
        'summary': {
            'total_files': len(results),
            'total_issues': total_issues,
            'by_severity': by_severity
        },
        'files': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)


def _report_html_multi(results: Dict[str, List], output_file: str):
    """Report results for multiple files to HTML"""
    total_issues = sum(len(issues) for issues in results.values())
    by_severity = {'critical': 0, 'error': 0, 'high': 0, 'warning': 0, 'info': 0}
    
    for issues in results.values():
        for issue in issues:
            severity = issue.get('severity', 'info')
            by_severity[severity] = by_severity.get(severity, 0) + 1
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>PyLint Pro Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .file-section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .critical {{ color: #d32f2f; font-weight: bold; }}
        .error {{ color: #f57c00; font-weight: bold; }}
        .high {{ color: #ffa726; }}
        .warning {{ color: #fbc02d; }}
        .info {{ color: #0288d1; }}
        .stats {{ display: flex; gap: 20px; margin-top: 15px; }}
        .stat-box {{ padding: 10px; border-radius: 4px; background: #f0f0f0; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        .issue {{ margin: 10px 0; padding: 10px; background: #fafafa; border-left: 3px solid #ddd; }}
    </style>
</head>
<body>
    <h1>PyLint Pro Analysis Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat-box"><strong>Files Analyzed:</strong> {len(results)}</div>
            <div class="stat-box"><strong>Total Issues:</strong> {total_issues}</div>
            <div class="stat-box"><strong>Critical:</strong> <span class="critical">{by_severity.get('critical', 0)}</span></div>
            <div class="stat-box"><strong>Errors:</strong> <span class="error">{by_severity.get('error', 0)}</span></div>
            <div class="stat-box"><strong>Warnings:</strong> <span class="warning">{by_severity.get('warning', 0)}</span></div>
        </div>
    </div>
"""
    
    for filepath, issues in results.items():
        if not issues:
            continue
            
        html += f"""
    <div class="file-section">
        <h2>{filepath}</h2>
"""
        for issue in issues:
            severity_class = issue.get('severity', 'info')
            html += f"""
        <div class="issue">
            <span class="{severity_class}">[{issue.get('severity', 'INFO').upper()}]</span>
            Line {issue.get('lineno', '?')}: {issue.get('message', 'No message')}
            <br><small>Type: {issue.get('type', 'unknown')}</small>
        </div>
"""
        html += "    </div>\n"
    
    html += """
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
