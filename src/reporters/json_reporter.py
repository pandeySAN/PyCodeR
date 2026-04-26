import json
from datetime import datetime


class JSONReporter:
    def __init__(self, issues, filename=None):
        self.issues = issues
        self.filename = filename
        
    def report(self, output_file=None):
        report_data = {
            'metadata': {
                'tool': 'PyLint Pro',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'analyzed_file': self.filename
            },
            'summary': self.get_summary(),
            'issues': self.format_issues()
        }
        
        json_output = json.dumps(report_data, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
        else:
            print(json_output)
            
        return json_output
        
    def get_summary(self):
        summary = {
            'total_issues': len(self.issues),
            'by_severity': {}
        }
        
        for issue in self.issues:
            severity = issue.get('severity', 'info')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
        return summary
        
    def format_issues(self):
        formatted = []
        for issue in self.issues:
            formatted.append({
                'type': issue.get('type', 'unknown'),
                'severity': issue.get('severity', 'info'),
                'line': issue.get('lineno'),
                'message': issue.get('message', ''),
                'name': issue.get('name'),
                'scope': issue.get('scope')
            })
        return formatted


def report_json(issues, filename=None, output_file=None):
    reporter = JSONReporter(issues, filename)
    return reporter.report(output_file)
