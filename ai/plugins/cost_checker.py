# ai/plugins/cost_checker.py
import os
import json

BUDGET_FILE = '.ai/budget.json'  # optional per-repo budget config

def load_budget():
    if os.path.exists(BUDGET_FILE):
        try:
            return json.load(open(BUDGET_FILE,'r',encoding='utf-8'))
        except:
            pass
    # fallback defaults (monthly in USD)
    return {'monthly_budget_usd': 50, 'monthly_spent_usd': 0}

def check_budget():
    b = load_budget()
    remaining = b['monthly_budget_usd'] - b.get('monthly_spent_usd',0)
    return {'monthly_budget_usd': b['monthly_budget_usd'], 'monthly_spent_usd': b.get('monthly_spent_usd',0), 'low_budget': remaining < 5}
