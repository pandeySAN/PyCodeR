from datetime import datetime


class HTMLReporter:
    def __init__(self, issues, filename=None):
        self.issues = issues
        self.filename = filename
        
    def report(self, output_file='report.html'):
        html = self.generate_html()
        
        with open(output_file, 'w') as f:
            f.write(html)
            
        return output_file
        
    def generate_html(self):
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>PyLint Pro Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .issue {{
            border-left: 4px solid #ccc;
            padding: 15px;
            margin: 15px 0;
            background: #fafafa;
        }}
        .critical {{ border-left-color: #d32f2f; }}
        .error {{ border-left-color: #f44336; }}
        .high {{ border-left-color: #ff9800; }}
        .warning {{ border-left-color: #ffc107; }}
        .info {{ border-left-color: #2196F3; }}
        .severity {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        .severity.critical {{ background: #d32f2f; }}
        .severity.error {{ background: #f44336; }}
        .severity.high {{ background: #ff9800; }}
        .severity.warning {{ background: #ffc107; color: #333; }}
        .severity.info {{ background: #2196F3; }}
        .line {{
            color: #666;
            font-size: 14px;
        }}
        .message {{
            margin: 10px 0;
            font-size: 15px;
        }}
        .type {{
            color: #888;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PyLint Pro Analysis Report</h1>
        
        {self.generate_metadata()}
        {self.generate_summary()}
        {self.generate_issues()}
    </div>
</body>
</html>"""
        
    def generate_metadata(self):
        return f"""
        <div class="metadata">
            <p><strong>File:</strong> {self.filename or 'N/A'}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """
        
    def generate_summary(self):
        total = len(self.issues)
        severity_counts = {}
        
        for issue in self.issues:
            sev = issue.get('severity', 'info')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
        summary_html = f"""
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Issues:</strong> {total}</p>
        """
        
        for severity in ['critical', 'error', 'high', 'warning', 'info']:
            if severity in severity_counts:
                count = severity_counts[severity]
                summary_html += f'<p><span class="severity {severity}">{severity.upper()}</span>: {count}</p>'
                
        summary_html += "</div>"
        return summary_html
        
    def generate_issues(self):
        if not self.issues:
            return "<p>No issues found!</p>"
            
        html = "<h2>Issues</h2>"
        
        for issue in self.issues:
            severity = issue.get('severity', 'info')
            lineno = issue.get('lineno', '?')
            message = issue.get('message', 'No message')
            issue_type = issue.get('type', 'unknown')
            
            html += f"""
            <div class="issue {severity}">
                <div>
                    <span class="severity {severity}">{severity.upper()}</span>
                    <span class="line">Line {lineno}</span>
                </div>
                <div class="message">{message}</div>
                <div class="type">Type: {issue_type}</div>
            </div>
            """
            
        return html


def report_html(issues, filename=None, output_file='report.html'):
    reporter = HTMLReporter(issues, filename)
    return reporter.report(output_file)
