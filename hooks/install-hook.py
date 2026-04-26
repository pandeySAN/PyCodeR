#!/usr/bin/env python3
"""
Pre-commit hook for PyLint Pro
Install: python hooks/install-hook.py
"""

import os
import sys
import shutil
from pathlib import Path


HOOK_SCRIPT = """#!/usr/bin/env python3
import subprocess
import sys

# Get list of staged Python files
result = subprocess.run(
    ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
    capture_output=True,
    text=True
)

python_files = [f for f in result.stdout.strip().split('\\n') if f.endswith('.py')]

if not python_files:
    sys.exit(0)

print("Running PyLint Pro on staged files...")

# Run pylint-pro on each file
exit_code = 0
for filepath in python_files:
    result = subprocess.run(
        ['pylint-pro', filepath, '--format', 'console'],
        capture_output=False
    )
    
    if result.returncode != 0:
        exit_code = 1

if exit_code != 0:
    print("\\n❌ PyLint Pro found issues. Commit aborted.")
    print("To bypass this check, use: git commit --no-verify")
    sys.exit(1)

print("✅ PyLint Pro check passed")
sys.exit(0)
"""


def install_hook():
    """Install pre-commit hook into .git/hooks/"""
    git_dir = Path('.git')
    
    if not git_dir.exists():
        print("Error: Not a git repository")
        sys.exit(1)
    
    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    hook_path = hooks_dir / 'pre-commit'
    
    if hook_path.exists():
        backup = hooks_dir / 'pre-commit.backup'
        shutil.copy(hook_path, backup)
        print(f"Backed up existing hook to {backup}")
    
    hook_path.write_text(HOOK_SCRIPT)
    hook_path.chmod(0o755)
    
    print(f"✓ Pre-commit hook installed at {hook_path}")
    print("PyLint Pro will now run on every commit")
    print("\nTo bypass: git commit --no-verify")


if __name__ == '__main__':
    install_hook()
