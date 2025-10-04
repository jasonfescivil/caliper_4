# LlamaIndex Dependency Management & Validation

## 📦 Dependency Strategy

> Packaging Decision: Option 1 (single Poetry project) with an optional `llamaindex` group and a separate `caliper_v2` console script. The v2 stack is only installed when explicitly requested (`poetry install --with llamaindex`), keeping the default environment lean and fast-suite friendly.

### Core Principles
1. Version pinning and hashes: pin exact versions; prefer Poetry lock; enable `virtualenvs.in-project = true`.
2. Compatibility matrix: track v1 (LangChain/FAISS) vs v2 (LlamaIndex) intersections.
3. Gradual migration: dual-stack until cutover; no breaking changes.
4. Security-first: automate `safety`/`pip-audit`; freeze base image; slim runtime.
5. Fast-suite friendly: mark heavy deps as optional groups; default install stays lean.

---

## 🔐 Dependency Version Matrix

### LlamaIndex Stack Requirements (Option 1 group-based)

The LlamaIndex-related dependencies live under an optional Poetry group `llamaindex`. This keeps v1 isolated and the default install lean. Align versions with root `pyproject.toml` caret pins to reduce churn while keeping compatibility.

Example (matches current root pyproject):
```toml
[tool.poetry.group.llamaindex]
optional = true

[tool.poetry.group.llamaindex.dependencies]
llama-index = "^0.11.0"
llama-index-core = "^0.11.0"
llama-index-readers-file = "^0.2.0"
llama-index-embeddings-openai = "^0.2.0"
llama-index-llms-openai = "^0.2.0"
llama-index-llms-anthropic = "^0.2.0"
llama-index-llms-gemini = "^0.2.0"
llama-index-llms-azure-openai = "^0.2.0"
httpx = "^0.27.0"
```

Install surfaces:
```bash
# Base (v1 only)
poetry install

# Enable v2 stack
poetry install --with llamaindex
```

Console scripts:
```toml
[tool.poetry.scripts]
caliper = "caliper.cli:app"         # v1
caliper_v2 = "caliper_v2.cli:app"   # v2 (LlamaIndex)
```

Group optional heavy extras so fast-suite remains fast:

```toml
[tool.poetry.group.llamaindex.optional]
[tool.poetry.group.llamaindex.dependencies]
llama-index-core = "0.11.22"
# ... other llama-index-* packages ...

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.1"
pytest-cov = "^5.0.0"
pytest-benchmark = "^4.0.0"
pip-audit = "^2.7.3"
safety = "^3.2.4"
```

### Compatibility Validation Script

With Option 1, validate that llama-index* are confined to the optional group, and that base install remains import-clean for v1:

```python
# validate_dependencies.py (excerpt – ensure llamaindex group isolation)
from __future__ import annotations
import toml
from pathlib import Path

data = toml.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
groups = data.get("tool", {}).get("poetry", {}).get("group", {})

llama_group = groups.get("llamaindex", {}).get("dependencies", {}) or {}
leaked = [k for k in deps.keys() if k.startswith("llama-index")]
if leaked:
    raise SystemExit(f"❌ llama-index packages leak into base deps: {leaked}")
print("✅ LlamaIndex deps isolated to optional group.")
```

```python
# validate_dependencies.py
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
import toml
from packaging.version import Version

PYPROJECT = Path("pyproject.toml")

class DependencyValidator:
    def __init__(self):
        data = toml.loads(PYPROJECT.read_text(encoding="utf-8"))
        self.deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        self.dev = data.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {}).get("dependencies", {})
        self.conflicts = []

    def validate(self) -> bool:
        print("🔍 Validating dependency compatibility...")
        # Example guardrails: ensure pinned exact versions for llama-index* and langchain
        for name, spec in self.deps.items():
            if name.startswith("llama-index") or name in ("langchain", "weaviate-client"):
                if not isinstance(spec, str) or any(c in spec for c in "^*>=<"):
                    self.conflicts.append({"package": name, "issue": f"Not pinned exactly: {spec}"})
        return len(self.conflicts) == 0

    def report(self):
        if not self.conflicts:
            print("✅ All dependencies compatible and pinned!")
        else:
            print("❌ Dependency issues found:")
            for c in self.conflicts:
                print(f"  - {c['package']}: {c['issue']}")

if __name__ == "__main__":
    ok = DependencyValidator().validate()
    DependencyValidator().report()
    sys.exit(0 if ok else 1)
```

---

## 🧪 Dependency Testing Matrix

### Environment Setup

```bash
# test_environments.sh
#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSIONS=("3.10" "3.11" "3.12")

for py_ver in "${PYTHON_VERSIONS[@]}"; do
  echo "Testing Python $py_ver"
  poetry env use python$py_ver
  poetry install --with dev --with llamaindex
  poetry run pytest -m "not slow" -q
  poetry run python - <<'PY'
try:
    import llama_index
    import langchain
    print("✅ Both frameworks imported successfully")
except Exception as e:
    print(f"❌ Import conflict: {e}")
    raise
PY
done
```

### Dependency Security Scanning

```python
# security_scan.py
from __future__ import annotations
import json
import subprocess
from typing import List, Dict

def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)

def scan_dependencies() -> List[Dict]:
    """Scan for vulnerabilities using safety and pip-audit."""
    vulns: List[Dict] = []

    safety = _run(["safety", "check", "--full-report", "--json"])
    if safety.stdout:
        try:
            for v in json.loads(safety.stdout):
                vulns.append({
                    "tool": "safety",
                    "package": v.get("package_name"),
                    "installed_version": v.get("affected_versions"),
                    "id": v.get("vuln_id"),
                    "severity": v.get("severity", "UNKNOWN"),
                    "fixed_version": v.get("fixed_versions"),
                })
        except Exception:
            pass

    audit = _run(["pip-audit", "--format", "json"])
    if audit.stdout:
        try:
            data = json.loads(audit.stdout)
            for v in data.get("vulnerabilities", []):
                vulns.append({
                    "tool": "pip-audit",
                    "package": v.get("name"),
                    "installed_version": v.get("version"),
                    "id": v.get("id"),
                    "severity": (v.get("fix_versions") and "HIGH") or "UNKNOWN",
                    "fixed_version": (v.get("fix_versions") or ["N/A"])[0],
                })
        except Exception:
            pass

    return vulns

def summarize(vulns: List[Dict]) -> str:
    if not vulns:
        return "✅ No security vulnerabilities found!"
    out = ["⚠️ Security Vulnerabilities Found:\n"]
    for v in vulns:
        out.append(f"- [{v['tool']}] {v['package']} {v['installed_version']} -> fix: {v['fixed_version']} ({v['id']})")
    return "\n".join(out)

if __name__ == "__main__":
    print(summarize(scan_dependencies()))
```

---

## 🔄 Gradual Dependency Migration Plan

### Phase 1: Parallel Installation (Option 1)
```bash
# Enable v2 stack side-by-side (no changes to v1)
poetry install --with llamaindex --with dev
# Verify v2 CLI is available:
poetry run caliper_v2 --help
```

### Phase 2: Feature Flags not Namespaces

Prefer feature flags/settings over importer hacks. Use Pydantic Settings:

With Option 1, use a runtime feature flag rather than import-time decisions. Keep heavy imports inside CLI commands or service methods to protect the fast-suite when the llamaindex group isn’t installed.

```python
# settings snippet
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    use_llamaindex: bool = False
    use_weaviate: bool = False
    embed_provider: str = "huggingface"  # or "openai"

settings = Settings()
```

Then branch at service boundaries, not import layers.

### Phase 3: Dependency Sunset Plan

```python
# sunset_tracker.py
from __future__ import annotations
from datetime import datetime, timedelta

class DependencySunset:
    """Track and manage v1 dependency sunset with feature flags and CI gates."""
    def __init__(self):
        self.sunset_schedule = {
            "langchain": datetime(2026, 1, 31),
            "custom_rag_modules": datetime(2025, 12, 31),
            "legacy_document_parsers": datetime(2025, 11, 30),
        }

    def check_sunset_status(self):
        now = datetime.now()
        report = []
        for dep, date in self.sunset_schedule.items():
            days = (date - now).days
            status = "ACTIVE"
            if days < 0: status = "OVERDUE FOR REMOVAL"
            elif days < 30: status = "REMOVE SOON"
            elif days < 90: status = "PLAN REMOVAL"
            report.append({"dependency": dep, "sunset_date": date.isoformat(), "days_until": days, "status": status})
        return report
```

---

## 🚀 Automated Dependency Updates

### Dependabot Configuration
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    labels: ["dependencies", "ll

This comprehensive dependency management ensures a smooth, secure migration without breaking existing functionality.
