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

def decide_mode(repo_path='.', user_force_mode=None):
    # 1) user override
    if user_force_mode:
        return RouterDecision(mode=user_force_mode, enabled_agents=mode_map[user_force_mode], reason="forced by user")

    # 2) project scan
    info = analyze_project(repo_path)

    # 3) cost check
    cost = check_budget()

    # 4) rule-based decision
    if cost.get('low_budget', False):
        return RouterDecision(mode='lite', enabled_agents=mode_map['lite'], reason='low budget')

    if info.get('is_enterprise', False) or info.get('has_payment', False) or info.get('touches_personal_data', False):
        return RouterDecision(mode='enterprise', enabled_agents=mode_map['enterprise'], reason='enterprise signals')

    if info.get('has_ui', False) or info.get('code_files', 0) > 50:
        return RouterDecision(mode='pro', enabled_agents=mode_map['pro'], reason='pro signals')

    return RouterDecision(mode='lite', enabled_agents=mode_map['lite'], reason='default fallback')
