# ai/plugins/project_scan.py
import os
import subprocess

def analyze_project(base_path='.'):
    # simple heuristics, extend later
    result = {
        'code_files': 0,
        'has_ui': False,
        'has_payment': False,
        'touches_personal_data': False,
        'is_enterprise': False,
        'changed_paths': [],
    }
    code_ext = ('.py','.ts','.js','.tsx','.jsx','.go','.java')
    ui_markers = ('components','pages','App.tsx','index.html')
    payment_markers = ('payments','stripe','paypal','billing')
    personal_markers = ('personal','ssn','social_security','passport','email')
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith(code_ext):
                result['code_files'] += 1
            if f in ui_markers:
                result['has_ui'] = True
            # fast checks in path names
            path = os.path.join(root, f).lower()
            if any(p in path for p in payment_markers):
                result['has_payment'] = True
            if any(p in path for p in personal_markers):
                result['touches_personal_data'] = True
    # enterprise heuristic
    if result['code_files'] > 500 or result['has_payment']:
        result['is_enterprise'] = True

    result['changed_paths'] = _detect_changed_paths(base_path)
    return result


def _detect_changed_paths(base_path: str):
    """Return a list of changed file paths relative to the repo."""
    try:
        output = subprocess.check_output(
            ['git', '-C', base_path, 'diff', '--name-only', 'origin/main...HEAD'],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return []

    return [line.strip() for line in output.splitlines() if line.strip()]
