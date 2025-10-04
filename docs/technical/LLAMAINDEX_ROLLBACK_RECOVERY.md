# LlamaIndex Migration Rollback & Recovery Plan

Aligned with Caliper rules: Docker-optional, Typer CLI, Loguru logging, SQLite persistence, FAISS default with optional Weaviate. All commands must be reproducible locally and in container.

Packaging Decision: Option 1 — single Poetry project with an optional `llamaindex` group and a separate `caliper_v2` console script. Rollback can be achieved by simply avoiding installation of the optional group and using v1 CLI (`caliper`) exclusively.

## 🔴 Emergency Procedures

### Immediate Rollback (< 5 minutes)

Option 1 enables a zero-change rollback by not enabling the v2 stack:

```bash
#!/usr/bin/env bash
# emergency_rollback.sh

set -euo pipefail
echo "🚨 INITIATING EMERGENCY ROLLBACK (Option 1)"

/usr/bin/env bash -c '
# Step 0: Ensure v2 stack is not present
poetry install --sync                       # base install only (no --with llamaindex)
echo "✅ Ensured base environment without llamaindex group"

# Step 1: Use v1 CLI only
if command -v poetry >/dev/null 2>&1; then
  poetry run caliper --help >/dev/null || true
fi
echo "✅ v1 CLI available (caliper)"

# Step 2: (Optional) enforce v1-only service behavior if engine flag exists
export DEFAULT_ENGINE=v1
echo "DEFAULT_ENGINE=v1" > /app/.env.override 2>/dev/null || true

# Step 3: Restart services if running in containers
docker compose restart app 2>/dev/null || docker-compose restart app 2>/dev/null || true

# Step 4: Verify
poetry run caliper diagnose --engine v1 2>/dev/null || true
'

echo "✅ Rollback complete. System running on v1 engine (v2 not installed)."
```

If the llamaindex group was previously installed and you want to remove it:

```bash
# Remove llamaindex artifacts from current venv by re-syncing without group
poetry install --sync
```

### Rollback Decision Matrix

| Symptom | Severity | Rollback? | Action |
|---------|----------|-----------|--------|
| Error rate > 10% | CRITICAL | Yes | Immediate rollback |
| p95 latency > 50% vs v1 | CRITICAL | Yes | Immediate rollback |
| Eval score drop > 10% (faithfulness/retrieval) | HIGH | Yes | Rollback and investigate |
| Data corruption detected | CRITICAL | Yes | Immediate + data recovery |
| Missing features | HIGH | No | Fix forward with fallback |
| UI inconsistencies | MEDIUM | No | Hot fix deployment |
| Increased latency 20–50% | MEDIUM | No | Performance tuning |

---

## 🔄 Rollback Procedures by Phase

### Phase 2 Rollback: Service Layer

For Option 1, service-layer rollback is primarily dependency-surface control and CLI selection:

```python
# rollback_phase2.py
import subprocess

class RollbackError(Exception): ...

def _run(cmd: str):
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        raise RollbackError(f"Failed at: {cmd}")

def rollback_service_layer():
    """Rollback service layer changes (Option 1)"""
    steps = [
        # Ensure base environment only (no llamaindex group)
        "poetry install --sync",
        # Prefer v1 CLI
        "poetry run caliper diagnose --full || true",
        # Clean optional caches if present
        "rm -rf /app/.cache/llamaindex || true",
    ]
    for step in steps:
        _run(step)
    return "Phase 2 rollback complete (Option 1)"
```

### Phase 3 Rollback: Integration

For Option 1, keep the separate CLI boundaries; do not route traffic to `caliper_v2`:

```python
# rollback_phase3.py
def rollback_integration():
    """Rollback CLI integration changes for Option 1."""
    # Ensure docs and runbooks direct users to v1 CLI only
    verify_v1_is_default()
    # No need to remove caliper_v2 entry; simply do not install llamaindex group
    verify_all_commands()
```

### Phase 4 Rollback: Production

```python
# rollback_phase4.py
def rollback_production():
    """Full production rollback with data preservation (Option 1)"""
    backup_current_state()
    # Rebuild runtime image without llamaindex group
    rebuild_lightweight_image_without_llamaindex()
    update_routing_to_v1()
    send_rollback_notifications()
```

---

## 💾 Data Recovery Procedures

### Vector Store Recovery
```python
# vector_store_recovery.py
from pathlib import Path
from datetime import datetime

class RecoveryError(Exception): ...

class VectorStoreRecovery:
    def __init__(self):
        self.backup_dir = Path("/backup/vector_stores")
        self.recovery_log = []

    def recover_to_checkpoint(self, checkpoint_date: datetime):
        """Recover vector store to specific checkpoint"""
        backup = self.find_backup(checkpoint_date)
        if not backup:
            raise RecoveryError(f"No backup found for {checkpoint_date}")
        self.stop_services()
        self.backup_current_state()
        self.restore_backup(backup)
        if not self.verify_integrity():
            raise RecoveryError("Integrity check failed after restore")
        self.start_services()
        return f"Recovered to checkpoint: {checkpoint_date}"

    def incremental_recovery(self):
        """Recover only corrupted vectors"""
        corrupted = self.identify_corrupted_vectors()
        for vector_id in corrupted:
            if self.recover_from_log(vector_id):
                continue
            self.reindex_document(vector_id)
```

### Document State Recovery
```python
# document_recovery.py
import sqlite3

def recover_document_state():
    """Recover document processing state"""
    conn = sqlite3.connect('/app/data/app.db')
    integrity = conn.execute("PRAGMA integrity_check").fetchone()
    if integrity[0] != "ok":
        restore_sqlite_backup()
    for doc in get_all_documents():
        stored_hash = get_stored_hash(doc.path)
        current_hash = calculate_hash(doc.path)
        if stored_hash != current_hash:
            mark_for_reprocessing(doc.path)
    reconcile_stores()
```

---

## 🛡️ Preventive Measures

### Option 1-specific Preventive Controls
- Keep LlamaIndex in optional Poetry group; do not include in caliper-light Docker image.
- Maintain `caliper_v2` as a separate console script; do not alter v1 commands during migration.
- Ensure lazy imports in v2 commands to avoid import errors when the group is not installed.
- CI: add a separate v2 lane (install with `--with llamaindex`) so v1 stays green if v2 fails.

### Canary Deployment
```python
# canary_deployment.py
import time

class CanaryDeployment:
    def __init__(self, canary_percentage: float = 0.1):
        self.canary_percentage = canary_percentage
        self.metrics_collector = MetricsCollector()

    def should_use_v2(self, user_id: str) -> bool:
        """Determine if user should use v2 using consistent hashing"""
        return hash(user_id) % 100 < (self.canary_percentage * 100)

    def monitor_canary_health(self):
        """Monitor canary deployment health using thresholds"""
        v1 = self.metrics_collector.get_metrics("v1")
        v2 = self.metrics_collector.get_metrics("v2")
        if v2.error_rate > v1.error_rate * 1.5:
            self.reduce_canary_traffic()
        if v2.p95_latency > v1.p95_latency * 1.2:
            self.alert_performance_issue()
        if hasattr(v2, "retrieval_acc") and hasattr(v1, "retrieval_acc"):
            if v2.retrieval_acc < v1.retrieval_acc * 0.9:
                self.reduce_canary_traffic()

    def gradual_rollout(self):
        """Gradually increase v2 traffic with health checks"""
        schedule = [0.1, 0.25, 0.5, 0.75, 1.0]
        for pct in schedule:
            self.canary_percentage = pct
            time.sleep(86400)  # 24h
            if not self.health_check_passed():
                self.rollback_canary()
                break
```

### Circuit Breaker Pattern
```python
# circuit_breaker.py
import time
from loguru import logger

class V2CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call_v2_service(self, operation, *args, **kwargs):
        """Call v2 service with circuit breaker protection"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                return self._fallback_to_v1(operation, *args, **kwargs)
        try:
            result = operation(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            if self.state == "OPEN":
                return self._fallback_to_v1(operation, *args, **kwargs)
            raise

    def _on_success(self):
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error("circuit_breaker_open")

    def _should_attempt_reset(self) -> bool:
        return (time.time() - (self.last_failure_time or 0)) >= self.timeout

    def _fallback_to_v1(self, operation, *args, **kwargs):
        # Implement or inject fallback handler
        return fallback_operation(*args, **kwargs)
```

---

## 📝 Rollback Runbook

### Pre-Rollback Checklist
- [ ] Identify root cause of issue (include latest eval metrics deltas)
- [ ] Backup current state (SQLite, vector store, outputs)
- [ ] Notify stakeholders
- [ ] Prepare rollback commands
- [ ] Ensure v1 system is ready (diagnose and smoke test)

### Rollback Execution
1. Initiate Rollback
   ```bash
   ./emergency_rollback.sh
   ```

2. **Verify Services**
   ```bash
   poetry run caliper diagnose --full
   ```

3. **Test Critical Functions**
   ```bash
   ./test_critical_functions.sh
   ```

4. **Monitor Metrics**
   ```bash
   ./monitor_rollback.sh
   ```

### Post-Rollback
- [ ] Document failure reasons with metrics and logs
- [ ] Create fix plan with eval targets
- [ ] Update test suite to cover the failure
- [ ] Plan re-deployment after burn-in
- [ ] Conduct retrospective

---

## 🔔 Communication Plan

### Stakeholder Notifications
```python
# notification_manager.py
class RollbackNotificationManager:
    def __init__(self):
        self.channels = {
            "slack": SlackNotifier(),
            "email": EmailNotifier(),
            "pagerduty": PagerDutyNotifier()
        }

    def notify_rollback_initiated(self, reason: str):
        message = f"""
        🔴 ROLLBACK INITIATED

        Reason: {reason}
        Time: {datetime.now().isoformat()}
        Affected Systems: Caliper v2 Engine
        Impact: Temporary reversion to v1 engine

        Action Required: None - automatic fallback active
        """

        for channel in self.channels.values():
            channel.send_urgent(message)

    def notify_rollback_complete(self, duration: float):
        message = f"""
        ✅ ROLLBACK COMPLETE

        Duration: {duration:.2f} seconds
        Current Engine: v1
        System Status: Operational

        Next Steps: Root cause analysis in progress
        """

        for channel in self.channels.values():
            channel.send_info(message)
```

This comprehensive rollback plan ensures system reliability and quick recovery from any migration issues.
