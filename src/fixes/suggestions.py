class SuggestionGenerator:
    def __init__(self, issues):
        self.issues = issues
        self.suggestions = []
        
    def generate(self):
        for issue in self.issues:
            suggestion = self.get_suggestion(issue)
            if suggestion:
                self.suggestions.append({
                    'issue': issue,
                    'suggestion': suggestion
                })
                
        return self.suggestions
        
    def get_suggestion(self, issue):
        issue_type = issue.get('type', '')
        
        if issue_type == 'unused_code':
            return "Remove unreachable code or fix control flow logic"
            
        elif issue_type == 'unused_variable':
            var_name = issue.get('name', 'variable')
            return f"Remove '{var_name}' or use it in your code"
            
        elif issue_type == 'unused_import':
            return "Remove unused import to reduce dependencies"
            
        elif issue_type == 'none_type_error':
            return "Add None check before calling method: if obj is not None: obj.method()"
            
        elif issue_type == 'sql_injection':
            return "Use parameterized queries instead of string concatenation"
            
        elif issue_type == 'hardcoded_password' or issue_type == 'hardcoded_secret':
            return "Move secrets to environment variables or config file"
            
        elif issue_type == 'dangerous_function':
            return "Avoid eval/exec - use safer alternatives like ast.literal_eval"
            
        elif issue_type == 'high_complexity':
            return "Break function into smaller functions to reduce complexity"
            
        elif issue_type == 'deep_nesting':
            return "Refactor to reduce nesting - consider early returns or extracting functions"
            
        elif issue_type == 'infinite_loop':
            return "Add break condition or ensure loop can exit"
            
        elif issue_type == 'arg_count_mismatch':
            return "Check function definition and call - argument count must match"
            
        return "Review and fix the issue"


class FixRecommendation:
    def __init__(self, issue, suggestion, priority):
        self.issue = issue
        self.suggestion = suggestion
        self.priority = priority
        
    def to_dict(self):
        return {
            'issue': self.issue,
            'suggestion': self.suggestion,
            'priority': self.priority
        }


def generate_suggestions(issues):
    generator = SuggestionGenerator(issues)
    return generator.generate()
