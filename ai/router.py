# ai/router.py
from dataclasses import dataclass
from ai.plugins.project_scan import analyze_project
from ai.plugins.cost_checker import check_budget
from ai.plugins.mode_map import mode_map

@dataclass
class RouterDecision:
    mode: str
    enabled_agents: list
    reason: str
    autofix_allowed: bool


def _autofix_permission(mode: str) -> bool:
    """Return whether autofix is permitted for the given mode."""
    if mode == 'pro':
        return True
    return False


def _touches_sensitive_paths(changed_paths):
    sensitive_prefixes = (
        'migrations/',
        'db/migrate/',
        'infra/',
        'terraform/',
        'k8s/',
        'auth/',
        'security/',
        'secrets/',
        'payment/',
        'billing/',
    )
    for path in changed_paths or []:
        lower_path = path.lower()
        if any(lower_path.startswith(prefix) for prefix in sensitive_prefixes):
            return True
    return False

def decide_mode(repo_path='.', user_force_mode=None):
    # 1) user override
    if user_force_mode:
        return RouterDecision(
            mode=user_force_mode,
            enabled_agents=mode_map[user_force_mode],
            reason="forced by user",
            autofix_allowed=_autofix_permission(user_force_mode)
        )

    # 2) project scan
    info = analyze_project(repo_path)

    # 3) cost check
    cost = check_budget()

    # 4) rule-based decision
    if _touches_sensitive_paths(info.get('changed_paths')):
        return RouterDecision(
            mode='enterprise',
            enabled_agents=mode_map['enterprise'],
            reason='sensitive paths touched',
            autofix_allowed=_autofix_permission('enterprise')
        )

    if cost.get('low_budget', False):
        return RouterDecision(mode='lite', enabled_agents=mode_map['lite'], reason='low budget', autofix_allowed=_autofix_permission('lite'))

    if info.get('is_enterprise', False) or info.get('has_payment', False) or info.get('touches_personal_data', False):
        return RouterDecision(mode='enterprise', enabled_agents=mode_map['enterprise'], reason='enterprise signals', autofix_allowed=_autofix_permission('enterprise'))

    if info.get('has_ui', False) or info.get('code_files', 0) > 50:
        return RouterDecision(mode='pro', enabled_agents=mode_map['pro'], reason='pro signals', autofix_allowed=_autofix_permission('pro'))

    return RouterDecision(mode='lite', enabled_agents=mode_map['lite'], reason='default fallback', autofix_allowed=_autofix_permission('lite'))
