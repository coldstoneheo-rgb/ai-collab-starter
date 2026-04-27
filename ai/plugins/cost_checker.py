# ai/plugins/cost_checker.py
import os
import json

BUDGET_FILE = '.ai/budget.json'  # optional per-repo budget config
LOW_BUDGET_THRESHOLD_USD = 5
WARN_THRESHOLD_RATIO = 0.8

def load_budget():
    if os.path.exists(BUDGET_FILE):
        try:
            with open(BUDGET_FILE, 'r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception:
            pass
    # fallback defaults (monthly in USD)
    return {'monthly_budget_usd': 50, 'monthly_spent_usd': 0}

def check_budget():
    b = load_budget()
    monthly_budget = b['monthly_budget_usd']
    monthly_spent = b.get('monthly_spent_usd', 0)
    remaining = monthly_budget - monthly_spent
    warn_threshold = monthly_budget * WARN_THRESHOLD_RATIO

    return {
        'monthly_budget_usd': monthly_budget,
        'monthly_spent_usd': monthly_spent,
        'remaining_usd': remaining,
        'low_budget': remaining < LOW_BUDGET_THRESHOLD_USD,
        'budget_warning': monthly_spent >= warn_threshold,
        'budget_exceeded': monthly_spent >= monthly_budget,
    }
