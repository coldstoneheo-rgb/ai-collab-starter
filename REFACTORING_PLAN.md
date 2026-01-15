# AI-Collab-Starter 리팩토링 실행 계획

**작성일**: 2026-01-15
**목표**: Phase 1 MVP 완성을 위한 실행 가능한 단계별 리팩토링 계획

---

## 목차

1. [즉시 실행 가능한 작업 (오늘)](#1-즉시-실행-가능한-작업-오늘)
2. [Sprint 1: Critical Implementation (Week 1-2)](#2-sprint-1-critical-implementation-week-1-2)
3. [Sprint 2: Governance & Safety (Week 3-4)](#3-sprint-2-governance--safety-week-3-4)
4. [Sprint 3: Polish & Production (Week 5-6)](#4-sprint-3-polish--production-week-5-6)
5. [체크리스트](#5-체크리스트)

---

## 1. 즉시 실행 가능한 작업 (오늘)

### 1.1 Python 패키지 구조 수정

**파일 생성**:
```bash
touch ai/__init__.py
touch ai/plugins/__init__.py
touch ai/runners/__init__.py
touch ai/runners/clients/__init__.py
touch ai/context7/__init__.py
touch ai/utils/__init__.py
```

**예상 시간**: 5분

---

### 1.2 requirements.txt 생성

**파일**: `/requirements.txt`

```txt
# Core AI SDKs
anthropic>=0.18.0
google-generativeai>=0.3.0
openai>=1.0.0

# RAG & Vector DB
chromadb>=0.4.0
sentence-transformers>=2.2.0

# GitHub Integration
PyGithub>=2.0.0
requests>=2.31.0

# Configuration
pyyaml>=6.0
python-dotenv>=1.0.0

# Utilities
python-dateutil>=2.8.2
```

**예상 시간**: 5분

---

### 1.3 Context 디렉토리 구조 생성

**스크립트**: `scripts/init_context_structure.sh`

```bash
#!/bin/bash

# Create Context structure
mkdir -p docs/CONTEXT/{business,compliance,architecture,uiux,data_model}

# Create README templates
cat > docs/CONTEXT/business/README.md <<'EOF'
# Business Logic & Domain Knowledge

This directory contains business logic documentation, domain models, and business rules.

## Contents

- Business workflows
- Domain terminology
- Business rules and constraints
- User stories and use cases

## Maintenance

- Update when business requirements change
- All changes require PR review
- Keep synchronized with PRD.md
EOF

cat > docs/CONTEXT/compliance/README.md <<'EOF'
# Compliance & Legal

This directory contains compliance requirements, legal constraints, and regulatory documentation.

## Contents

- Legal requirements
- Privacy policies (GDPR, COPPA, etc.)
- Security standards
- Regulatory compliance

## Maintenance

- Review quarterly
- Changes require legal team approval
- Document all regulatory changes
EOF

cat > docs/CONTEXT/architecture/README.md <<'EOF'
# Architecture & System Design

This directory contains system architecture documentation, API specifications, and design decisions.

## Contents

- System architecture diagrams
- API specifications (OpenAPI)
- Database schemas
- Integration patterns

## Maintenance

- Update with every major architectural change
- All changes require architecture review
- Keep synchronized with actual code
EOF

cat > docs/CONTEXT/uiux/README.md <<'EOF'
# UI/UX Design

This directory contains UI/UX design guidelines, component specifications, and user flows.

## Contents

- Design system
- Component specifications
- User flows
- Accessibility guidelines

## Maintenance

- Update with design changes
- Changes require UX review
- Keep synchronized with frontend code
EOF

cat > docs/CONTEXT/data_model/README.md <<'EOF'
# Data Models

This directory contains database schemas, data models, and data contracts.

## Contents

- Database schemas
- Entity relationships
- Data contracts
- Migration history

## Maintenance

- Update with every schema change
- All changes require data team review
- Document migration strategies
EOF

# Create project-level context files
cat > docs/project_vision.md <<'EOF'
# Project Vision

## Mission

[Define project mission]

## Goals

[Define project goals]

## Success Criteria

[Define measurable success criteria]

## Roadmap

[High-level roadmap]
EOF

cat > docs/compliance.md <<'EOF'
# Compliance Overview

## Applicable Regulations

[List applicable regulations]

## Compliance Requirements

[Detail compliance requirements]

## Monitoring

[How compliance is monitored]
EOF

echo "Context structure created successfully!"
```

**실행**:
```bash
chmod +x scripts/init_context_structure.sh
./scripts/init_context_structure.sh
```

**예상 시간**: 10분

---

### 1.4 AI Team Configuration 생성

**파일**: `.github/ai_team.yml`

```yaml
project_name: ai-collab-starter
version: 1.0
description: AI Multi-Agent Collaboration Starter Template

team:
  pm:
    agent: claude
    model: claude-sonnet-4-5-20250929
    responsibilities:
      - product_requirement_review
      - acceptance_criteria_validation
      - architecture_review
      - security_review
      - release_planning
    prompt_template: claude_pm_review_v1.txt

  frontend_lead:
    agent: gemini
    model: gemini-2.0-flash-thinking-exp-01-21
    responsibilities:
      - uiux_design_review
      - component_structure_analysis
      - responsiveness_check
      - accessibility_validation
      - multi_perspective_analysis
    prompt_template: gemini_uiux_v1.txt

  compliance:
    agent: perplexity
    model: llama-3.1-sonar-large-128k-online
    responsibilities:
      - legal_review
      - policy_compliance_check
      - risk_analysis
      - regulatory_validation
      - market_research
    prompt_template: perplexity_compliance_v1.txt

  backend_engineer:
    agent: gpt
    model: gpt-4.5-preview
    responsibilities:
      - api_design_review
      - database_schema_review
      - infrastructure_review
      - devops_review
      - performance_analysis
      - technical_documentation
    prompt_template: gpt_backend_v1.txt

rules:
  merge_requires:
    - pm  # Claude PM review always required
    - frontend_lead  # Gemini FE review for UI changes

  enterprise_required_for_paths:
    - "infra/**"
    - "terraform/**"
    - "k8s/**"
    - "security/**"
    - "auth/**"
    - "payments/**"
    - "migrations/**"
    - ".github/workflows/**"

  autofix_enabled:
    - lint_fixes
    - formatting
    - simple_refactoring

  autofix_disabled:
    - security_changes
    - database_migrations
    - infrastructure_changes
    - api_contract_changes

budget:
  monthly_limit_usd: 50
  alert_threshold_percent: 80
  cost_per_mode:
    lite: 0.20
    pro: 0.75
    enterprise: 2.50

monitoring:
  metrics_enabled: true
  audit_logs_retention_days: 90
  alert_channels:
    - github_issues
    # - slack  # Uncomment when configured
    # - email  # Uncomment when configured
```

**예상 시간**: 10분

---

### 1.5 Budget Configuration 템플릿

**파일**: `.ai/budget.json`

```json
{
  "monthly_budget_usd": 50,
  "monthly_spent_usd": 0,
  "last_reset": "2026-01-01",
  "cost_tracking": {
    "claude": 0,
    "gemini": 0,
    "perplexity": 0,
    "gpt": 0
  },
  "history": []
}
```

**디렉토리 생성**:
```bash
mkdir -p .ai
```

**예상 시간**: 2분

---

### 1.6 Prompt 파일 리네임

**작업**:
```bash
cd .github/AI_PROMPTS/

# Rename with version suffixes
mv claude_review.txt claude_pm_review_v1.txt
mv gemini_uiux.txt gemini_uiux_v1.txt
mv perplexity_compliance.txt perplexity_compliance_v1.txt
mv autofix.txt autofix_v1.txt
```

**예상 시간**: 2분

---

## 2. Sprint 1: Critical Implementation (Week 1-2)

### 2.1 PR Diff Collector 구현

**파일**: `ai/utils/pr_collector.py`

```python
#!/usr/bin/env python3
"""
GitHub PR information collector using PyGithub.
"""
import os
from typing import Dict, List, Optional
from github import Github, PullRequest
from dataclasses import dataclass


@dataclass
class PRInfo:
    """PR information container."""
    number: int
    title: str
    body: str
    author: str
    base_ref: str
    head_ref: str
    diff: str
    changed_files: List[str]
    commits: List[Dict[str, str]]


def collect_pr_info(pr_number: int, repo_name: str, token: Optional[str] = None) -> PRInfo:
    """
    Collect comprehensive PR information from GitHub.

    Args:
        pr_number: PR number
        repo_name: Repository name in format "owner/repo"
        token: GitHub token (or uses GITHUB_TOKEN env var)

    Returns:
        PRInfo object with all PR details
    """
    if not token:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GitHub token required (GITHUB_TOKEN env or token param)")

    g = Github(token)
    repo = g.get_repo(repo_name)
    pr: PullRequest.PullRequest = repo.get_pull(pr_number)

    # Collect diff
    import requests
    diff_url = pr.diff_url
    diff_response = requests.get(diff_url, headers={'Authorization': f'token {token}'})
    diff = diff_response.text if diff_response.ok else ""

    # Collect changed files
    changed_files = [f.filename for f in pr.get_files()]

    # Collect commits
    commits = [
        {
            'sha': c.sha[:7],
            'message': c.commit.message,
            'author': c.commit.author.name
        }
        for c in pr.get_commits()
    ]

    return PRInfo(
        number=pr.number,
        title=pr.title,
        body=pr.body or "",
        author=pr.user.login,
        base_ref=pr.base.ref,
        head_ref=pr.head.ref,
        diff=diff,
        changed_files=changed_files,
        commits=commits
    )


def post_pr_comment(pr_number: int, repo_name: str, comment: str, token: Optional[str] = None):
    """
    Post a comment on a PR.

    Args:
        pr_number: PR number
        repo_name: Repository name
        comment: Comment text
        token: GitHub token
    """
    if not token:
        token = os.getenv('GITHUB_TOKEN')

    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(comment)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: pr_collector.py <repo> <pr_number>")
        sys.exit(1)

    info = collect_pr_info(int(sys.argv[2]), sys.argv[1])
    print(f"PR #{info.number}: {info.title}")
    print(f"Changed files: {len(info.changed_files)}")
    print(f"Commits: {len(info.commits)}")
```

**테스트**:
```bash
python ai/utils/pr_collector.py coldstoneheo-rgb/ai-collab-starter 6
```

**예상 시간**: 4-6시간

---

### 2.2 AI Client 공통 인터페이스

**파일**: `ai/runners/clients/base_client.py`

```python
#!/usr/bin/env python3
"""
Abstract base class for AI clients.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AIResponse:
    """Standardized AI response."""
    content: str
    raw_response: Any
    model: str
    tokens_used: int
    cost_usd: float
    metadata: Dict[str, Any]


class AIClient(ABC):
    """Base class for all AI clients."""

    def __init__(self, api_key: Optional[str] = None, model: str = ""):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def send_prompt(self, prompt: str, **kwargs) -> AIResponse:
        """Send prompt to AI and get response."""
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str) -> float:
        """Estimate cost of sending this prompt."""
        pass

    def _count_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token)."""
        return len(text) // 4
```

**예상 시간**: 1시간

---

### 2.3 Claude API Client 구현

**파일**: `ai/runners/clients/claude_client.py`

```python
#!/usr/bin/env python3
"""
Claude API client implementation.
"""
import os
from typing import Optional, Dict, Any
from anthropic import Anthropic
from .base_client import AIClient, AIResponse


class ClaudeClient(AIClient):
    """Claude API client using Anthropic SDK."""

    # Cost per 1M tokens (input/output)
    COST_PER_1M_INPUT = 3.00
    COST_PER_1M_OUTPUT = 15.00

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        super().__init__(api_key or os.getenv('CLAUDE_API_KEY'), model)
        self.client = Anthropic(api_key=self.api_key)

    def send_prompt(self, prompt: str, max_tokens: int = 4000, **kwargs) -> AIResponse:
        """
        Send prompt to Claude API.

        Args:
            prompt: The prompt text
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters

        Returns:
            AIResponse object
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )

            # Extract content
            content = response.content[0].text if response.content else ""

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (
                (input_tokens / 1_000_000) * self.COST_PER_1M_INPUT +
                (output_tokens / 1_000_000) * self.COST_PER_1M_OUTPUT
            )

            return AIResponse(
                content=content,
                raw_response=response,
                model=self.model,
                tokens_used=input_tokens + output_tokens,
                cost_usd=cost,
                metadata={
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'stop_reason': response.stop_reason
                }
            )

        except Exception as e:
            raise RuntimeError(f"Claude API error: {e}")

    def estimate_cost(self, prompt: str) -> float:
        """Estimate cost based on prompt length."""
        input_tokens = self._count_tokens(prompt)
        # Assume output is 50% of input
        output_tokens = input_tokens // 2
        return (
            (input_tokens / 1_000_000) * self.COST_PER_1M_INPUT +
            (output_tokens / 1_000_000) * self.COST_PER_1M_OUTPUT
        )


if __name__ == '__main__':
    # Test
    client = ClaudeClient()
    response = client.send_prompt("Say hello in one sentence.")
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost_usd:.4f}")
    print(f"Tokens: {response.tokens_used}")
```

**예상 시간**: 6-8시간

---

### 2.4 Gemini API Client 구현

**파일**: `ai/runners/clients/gemini_client.py`

```python
#!/usr/bin/env python3
"""
Gemini API client implementation.
"""
import os
from typing import Optional
import google.generativeai as genai
from .base_client import AIClient, AIResponse


class GeminiClient(AIClient):
    """Gemini API client using Google SDK."""

    # Approximate cost per 1M tokens
    COST_PER_1M_INPUT = 0.50
    COST_PER_1M_OUTPUT = 1.50

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-thinking-exp-01-21"):
        super().__init__(api_key or os.getenv('GEMINI_API_KEY'), model)
        genai.configure(api_key=self.api_key)
        self.model_instance = genai.GenerativeModel(self.model)

    def send_prompt(self, prompt: str, **kwargs) -> AIResponse:
        """Send prompt to Gemini API."""
        try:
            response = self.model_instance.generate_content(prompt, **kwargs)

            content = response.text if hasattr(response, 'text') else str(response)

            # Token counting (approximate)
            input_tokens = self._count_tokens(prompt)
            output_tokens = self._count_tokens(content)
            total_tokens = input_tokens + output_tokens

            cost = (
                (input_tokens / 1_000_000) * self.COST_PER_1M_INPUT +
                (output_tokens / 1_000_000) * self.COST_PER_1M_OUTPUT
            )

            return AIResponse(
                content=content,
                raw_response=response,
                model=self.model,
                tokens_used=total_tokens,
                cost_usd=cost,
                metadata={
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens
                }
            )

        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

    def estimate_cost(self, prompt: str) -> float:
        """Estimate cost."""
        input_tokens = self._count_tokens(prompt)
        output_tokens = input_tokens // 2
        return (
            (input_tokens / 1_000_000) * self.COST_PER_1M_INPUT +
            (output_tokens / 1_000_000) * self.COST_PER_1M_OUTPUT
        )


if __name__ == '__main__':
    client = GeminiClient()
    response = client.send_prompt("Say hello in one sentence.")
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost_usd:.4f}")
```

**예상 시간**: 4-6시간

---

### 2.5 Runner 리팩토링

**파일**: `ai/runners/run_claude_review.py` (수정)

```python
#!/usr/bin/env python3
"""
Claude PM review runner - production version.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from ai.context7.rag_pipeline import fetch_top_k
from ai.utils.pr_collector import collect_pr_info, post_pr_comment
from ai.runners.clients.claude_client import ClaudeClient
from ai.utils.audit_logger import log_ai_action


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr-number', type=int, required=True)
    parser.add_argument('--repo', type=str, default=os.getenv('GITHUB_REPOSITORY'))
    parser.add_argument('--output', type=str, default='claude_output.json')
    args = parser.parse_args()

    # Collect PR info
    pr_info = collect_pr_info(args.pr_number, args.repo)

    # Fetch RAG context
    top_docs = fetch_top_k(f"{pr_info.title} {pr_info.body}", k=5)

    # Load prompt template
    template_path = Path('.github/AI_PROMPTS/claude_pm_review_v1.txt')
    template = template_path.read_text()

    # Build prompt
    context_text = "\n\n".join([f"## {d['path']}\n{d['content'][:500]}" for d in top_docs])

    prompt = f"""{template}

## PR Information
Title: {pr_info.title}
Author: {pr_info.author}
Description: {pr_info.body}

## Changed Files
{chr(10).join(pr_info.changed_files)}

## Diff
```diff
{pr_info.diff[:10000]}  # Limit diff size
```

## Project Context
{context_text}
"""

    # Send to Claude
    client = ClaudeClient()
    response = client.send_prompt(prompt)

    # Parse response (assume JSON)
    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {
            "verdict": "REVISE_REQUIRED",
            "issues": [{"severity": "error", "description": "Failed to parse AI response"}],
            "tests": [],
            "summary": response.content[:500]
        }

    # Log to audit
    log_ai_action(
        agent='claude',
        pr_number=args.pr_number,
        prompt=prompt,
        response=response.content,
        cost=response.cost_usd,
        model=response.model
    )

    # Post PR comment
    comment = f"""## 🤖 Claude PM Review

**Verdict**: {result['verdict']}

**Issues**: {len(result.get('issues', []))}

**Details**: {result.get('summary', 'See full review')}

Cost: ${response.cost_usd:.4f} | Tokens: {response.tokens_used}
"""
    post_pr_comment(args.pr_number, args.repo, comment)

    # Write output
    output = {
        **result,
        'cost_usd': response.cost_usd,
        'tokens_used': response.tokens_used,
        'model': response.model
    }
    Path(args.output).write_text(json.dumps(output, indent=2))

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
```

**유사하게 Gemini, Perplexity, GPT runner 리팩토링**

**예상 시간**: 2-3일

---

## 3. Sprint 2: Governance & Safety (Week 3-4)

### 3.1 Audit Logger 구현

**파일**: `ai/utils/audit_logger.py`

```python
#!/usr/bin/env python3
"""
Audit logging system for AI actions.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


LOG_DIR = Path('ai/logs')


def log_ai_action(
    agent: str,
    pr_number: int,
    prompt: str,
    response: str,
    cost: float,
    model: str,
    metadata: Optional[dict] = None
):
    """
    Log AI action to append-only audit log.

    Args:
        agent: AI agent name (claude, gemini, etc.)
        pr_number: PR number
        prompt: Full prompt sent
        response: Full response received
        cost: Cost in USD
        model: Model name
        metadata: Additional metadata
    """
    # Create date-based directory
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_dir = LOG_DIR / date_str
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create log entry
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'agent': agent,
        'pr_number': pr_number,
        'model': model,
        'cost_usd': cost,
        'prompt': prompt,
        'response': response,
        'metadata': metadata or {}
    }

    # Write to file (append-only)
    log_file = log_dir / f"{timestamp}_{pr_number}_{agent}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)

    print(f"Logged to: {log_file}")


def get_logs(date: Optional[str] = None, agent: Optional[str] = None):
    """Retrieve logs by date and/or agent."""
    if date:
        log_dir = LOG_DIR / date
    else:
        log_dir = LOG_DIR

    logs = []
    for log_file in log_dir.glob('**/*.json'):
        if agent and agent not in log_file.name:
            continue
        with open(log_file, 'r', encoding='utf-8') as f:
            logs.append(json.load(f))

    return logs
```

**예상 시간**: 4시간

---

### 3.2 Kill-Switch 구현

**파일**: `ai/router.py` (수정)

```python
def decide_mode(repo_path='.', user_force_mode=None):
    # 0) Emergency kill-switch check
    kill_switch = os.getenv('DISABLE_AI_AUTOMATION', '').lower()
    if kill_switch == 'true':
        raise RuntimeError(
            "🚨 AI Automation is DISABLED by emergency kill-switch.\n"
            "Set DISABLE_AI_AUTOMATION=false to re-enable."
        )

    # ... rest of function ...
```

**Workflow 수정**: `.github/workflows/ai_review.yml`

```yaml
router:
  needs: index
  runs-on: ubuntu-latest
  outputs:
    mode: ${{ steps.decide.outputs.mode }}
    enabled_agents: ${{ steps.decide.outputs.enabled_agents }}
    autofix_allowed: ${{ steps.decide.outputs.autofix_allowed }}
  steps:
    - uses: actions/checkout@v4
    - name: Check kill-switch
      run: |
        if [ "${{ secrets.DISABLE_AI_AUTOMATION }}" == "true" ]; then
          echo "🚨 AI Automation disabled by kill-switch"
          exit 1
        fi
    # ... rest of job ...
```

**예상 시간**: 2시간

---

### 3.3 Cost Enforcement

**파일**: `ai/utils/cost_tracker.py`

```python
#!/usr/bin/env python3
"""
Cost tracking and enforcement.
"""
import json
from pathlib import Path
from datetime import datetime
from threading import Lock

BUDGET_FILE = Path('.ai/budget.json')
LOCK = Lock()


def track_cost(agent: str, cost_usd: float):
    """
    Track cost and update budget file.

    Args:
        agent: AI agent name
        cost_usd: Cost in USD
    """
    with LOCK:
        budget = json.loads(BUDGET_FILE.read_text())

        # Update totals
        budget['monthly_spent_usd'] += cost_usd
        budget['cost_tracking'][agent] += cost_usd

        # Add to history
        budget['history'].append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent,
            'cost_usd': cost_usd
        })

        # Write back
        BUDGET_FILE.write_text(json.dumps(budget, indent=2))

        # Check budget
        remaining = budget['monthly_budget_usd'] - budget['monthly_spent_usd']
        if remaining <= 0:
            raise RuntimeError(
                f"💰 Budget exceeded!\n"
                f"Spent: ${budget['monthly_spent_usd']:.2f} / ${budget['monthly_budget_usd']:.2f}"
            )

        if remaining < 5:
            print(f"⚠️ Low budget warning: ${remaining:.2f} remaining")


if __name__ == '__main__':
    # Test
    track_cost('claude', 0.05)
    print("Cost tracked successfully")
```

**통합**: 모든 runner에서 `track_cost()` 호출

**예상 시간**: 4시간

---

## 4. Sprint 3: Polish & Production (Week 5-6)

### 4.1 Status Check 개선

**Workflow 수정** (예시):

```yaml
claude_review:
  needs: router
  if: contains(fromJson(needs.router.outputs.enabled_agents), 'claude')
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run Claude Review
      id: review
      env:
        CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_REPOSITORY: ${{ github.repository }}
      run: |
        python ai/runners/run_claude_review.py \
          --pr-number ${{ github.event.pull_request.number }} \
          --repo ${{ github.repository }} \
          --output claude_output.json

    - name: Create Claude status check
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const output = JSON.parse(fs.readFileSync('claude_output.json', 'utf8'));

          const conclusion = output.verdict === 'APPROVE' ? 'success' : 'failure';
          const summary = `**Verdict**: ${output.verdict}\n\n**Issues**: ${output.issues.length}`;

          await github.rest.checks.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            name: 'Claude PM Review',
            head_sha: context.payload.pull_request.head.sha,
            status: 'completed',
            conclusion: conclusion,
            output: {
              title: 'Claude PM Review',
              summary: summary,
              text: JSON.stringify(output.issues, null, 2)
            }
          });
```

**예상 시간**: 1일

---

### 4.2 Unit Tests

**파일**: `tests/test_router.py`

```python
import pytest
from ai.router import decide_mode, _touches_sensitive_paths


def test_decide_mode_lite():
    """Test lite mode selection."""
    # Mock cost checker to return low budget
    decision = decide_mode()
    assert decision.mode in ['lite', 'pro', 'enterprise']


def test_sensitive_paths():
    """Test sensitive path detection."""
    assert _touches_sensitive_paths(['infra/main.tf'])
    assert _touches_sensitive_paths(['security/auth.py'])
    assert not _touches_sensitive_paths(['src/app.py'])


def test_user_override():
    """Test user mode override."""
    decision = decide_mode(user_force_mode='enterprise')
    assert decision.mode == 'enterprise'
    assert decision.reason == 'forced by user'
```

**파일**: `tests/test_plugins.py`

```python
import pytest
from ai.plugins.project_scan import analyze_project
from ai.plugins.cost_checker import check_budget


def test_project_scan():
    """Test project scan."""
    result = analyze_project('.')
    assert 'code_files' in result
    assert isinstance(result['code_files'], int)


def test_cost_checker():
    """Test budget checker."""
    result = check_budget()
    assert 'low_budget' in result
    assert isinstance(result['low_budget'], bool)
```

**실행**:
```bash
pytest tests/ -v
```

**예상 시간**: 2-3일

---

## 5. 체크리스트

### 5.1 Phase 1 완성 체크리스트

#### **Infrastructure**
- [ ] `__init__.py` 모든 디렉토리
- [ ] `requirements.txt` 생성
- [ ] Context 구조 생성
- [ ] AI Team YAML 생성
- [ ] Budget JSON 생성

#### **API Integration**
- [ ] Base client 인터페이스
- [ ] Claude client 완성
- [ ] Gemini client 완성
- [ ] Perplexity client 완성
- [ ] GPT client 완성

#### **Runners**
- [ ] `run_claude_review.py` 리팩토링
- [ ] `run_gemini_review.py` 리팩토링
- [ ] `run_perplexity_review.py` 리팩토링
- [ ] `run_gpt_review.py` 구현

#### **Utilities**
- [ ] PR collector 구현
- [ ] Audit logger 구현
- [ ] Cost tracker 구현
- [ ] Prompt loader 구현
- [ ] Team config parser 구현

#### **Governance**
- [ ] Kill-switch 구현
- [ ] Cost enforcement 구현
- [ ] Sensitive path detection 확인
- [ ] Branch protection 설정
- [ ] Status checks 개선

#### **Testing**
- [ ] Router unit tests
- [ ] Plugin unit tests
- [ ] Client unit tests
- [ ] Integration test (1 PR)
- [ ] 50 PR 파일럿 테스트

#### **Documentation**
- [ ] API Reference
- [ ] Developer Guide
- [ ] Deployment Guide
- [ ] Troubleshooting Guide

---

### 5.2 Phase 1 Gate Criteria

Phase 1 완료 판정 기준 (CLAUDE.md §13):

- [ ] PR 성공률 ≥ 95% (최근 50 PRs)
- [ ] AI 제안 거부율 ≤ 30% (최근 30 PRs)
- [ ] PR당 평균 비용 ≤ $1
- [ ] Audit logs 100+ actions 보관
- [ ] Emergency kill-switch 작동 검증
- [ ] Cost enforcement 작동 검증
- [ ] 모든 AI agent 실제 리뷰 동작
- [ ] Status checks 정확히 pass/fail
- [ ] PR 코멘트 자동 생성
- [ ] 문서화 완료

---

### 5.3 다음 단계 (Phase 2 준비)

Phase 1 완료 후:

- [ ] Chroma 벡터 DB 통합 계획
- [ ] Metrics collection 설계
- [ ] Dashboard 프로토타입
- [ ] Compare reports 설계
- [ ] Alert system 설계

---

## 마무리

이 계획은 **실행 가능한 단계별 가이드**입니다.

**첫 주 목표**:
1. Infrastructure 준비 (오늘)
2. PR collector 구현 (Day 2-3)
3. Claude client 구현 (Day 4-5)

**두 번째 주 목표**:
1. 모든 client 완성
2. Runners 리팩토링
3. 첫 실제 리뷰 동작 확인

**진행 방식**:
- 매일 체크리스트 업데이트
- 작업 완료 시 Git commit
- 주간 진행 상황 리뷰

**성공 지표**:
- 6주 내 Phase 1 완성
- 실제 프로젝트 적용 가능
- Gate criteria 충족

---

*문서 끝 - 이제 실행하세요!*
