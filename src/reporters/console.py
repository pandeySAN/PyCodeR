class ConsoleReporter:
    def __init__(self, issues, filename=None):
        self.issues = issues
        self.filename = filename
        self.colors = {
            'critical': '\033[91m',
            'error': '\033[91m',
            'high': '\033[93m',
            'warning': '\033[93m',
            'info': '\033[94m',
            'reset': '\033[0m'
        }
        
    def report(self):
        if not self.issues:
            print(f"\n✓ No issues found in {self.filename or 'code'}")
            return
            
        print(f"\n{'='*60}")
        print(f"PyLint Pro Analysis Report")
        if self.filename:
            print(f"File: {self.filename}")
        print(f"{'='*60}\n")
        
        grouped = self.group_by_severity()
        
        for severity in ['critical', 'error', 'high', 'warning', 'info']:
            if severity in grouped:
                self.print_severity_group(severity, grouped[severity])
                
        self.print_summary()
        
    def group_by_severity(self):
        grouped = {}
        for issue in self.issues:
            severity = issue.get('severity', 'info')
            if severity not in grouped:
                grouped[severity] = []
            grouped[severity].append(issue)
        return grouped
        
    def print_severity_group(self, severity, issues):
        color = self.colors.get(severity, self.colors['reset'])
        reset = self.colors['reset']
        
        print(f"{color}{severity.upper()}{reset} ({len(issues)} issues)")
        print("-" * 60)
        
        for issue in issues:
            lineno = issue.get('lineno', '?')
            msg = issue.get('message', 'No message')
            issue_type = issue.get('type', 'unknown')
            
            print(f"  Line {lineno}: {msg}")
            print(f"    Type: {issue_type}")
            print()
            
    def print_summary(self):
        print("=" * 60)
        total = len(self.issues)
        
        severity_counts = {}
        for issue in self.issues:
            sev = issue.get('severity', 'info')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
        print(f"Total Issues: {total}")
        for severity, count in severity_counts.items():
            print(f"  {severity}: {count}")
        print("=" * 60)


def report_console(issues, filename=None):
    reporter = ConsoleReporter(issues, filename)
    reporter.report()
