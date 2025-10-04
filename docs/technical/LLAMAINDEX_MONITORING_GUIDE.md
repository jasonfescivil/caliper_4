# LlamaIndex Migration Monitoring & Observability

Aligned to Caliper logging/metrics rules: use Loguru logger, export Prometheus metrics, and track RAG-specific evals (faithfulness/relevancy, retrieval hit rate). No print(); CLI uses Typer for human-readable output.

## 📊 Key Metrics to Track

### Performance & Quality Metrics

```python
# metrics.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import time
from prometheus_client import Counter, Histogram, Gauge
from loguru import logger

# Prometheus primitives
REQ_TOTAL = Counter("caliper_queries_total", "Total queries", ["engine", "operation"])
ERR_TOTAL = Counter("caliper_errors_total", "Total errors", ["engine", "operation"])
FALLBACK_TOTAL = Counter("caliper_fallbacks_total", "Total fallbacks", ["operation"])
DURATION = Histogram(
    "caliper_query_duration_seconds",
    "Operation duration in seconds",
    ["engine", "operation"],
    buckets=(0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5, 8, 13),
)
RETRIEVAL_ACCURACY = Gauge("caliper_retrieval_accuracy", "Retrieval accuracy (0-1)", ["split"])
EVAL_FAITHFULNESS = Gauge("caliper_eval_faithfulness", "Faithfulness score (0-1)", ["split"])

@dataclass
class QueryMetrics:
    query_id: str
    engine: str  # "v1" or "llamaindex"
    operation: str  # "query", "ingest", "template"
    start_time: float
    end_time: float
    success: bool
    fallback_used: bool
    error_message: str = ""

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    @property
    def latency_ms(self) -> int:
        return int(self.duration * 1000)

class MetricsCollector:
    def __init__(self):
        self.thresholds = {
            "query_latency_ms": 2000,
            "ingest_latency_ms": 5000,
            "error_rate_percent": 2.0,
            "fallback_rate_percent": 5.0,
            "eval_drop_percent": 10.0,  # fail if eval metrics worsen >10%
        }
        self._window: List[QueryMetrics] = []

    def record(self, metric: QueryMetrics) -> None:
        REQ_TOTAL.labels(engine=metric.engine, operation=metric.operation).inc()
        DURATION.labels(engine=metric.engine, operation=metric.operation).observe(metric.duration)
        if metric.fallback_used:
            FALLBACK_TOTAL.labels(operation=metric.operation).inc()
        if not metric.success:
            ERR_TOTAL.labels(engine=metric.engine, operation=metric.operation).inc()

        self._window.append(metric)
        self._check_thresholds(metric)

    def record_eval_scores(self, retrieval_acc: Optional[float] = None, faithfulness: Optional[float] = None, split: str = "shadow") -> None:
        if retrieval_acc is not None:
            RETRIEVAL_ACCURACY.labels(split=split).set(retrieval_acc)
        if faithfulness is not None:
            EVAL_FAITHFULNESS.labels(split=split).set(faithfulness)

    def _check_thresholds(self, metric: QueryMetrics) -> None:
        op_key = f"{metric.operation}_latency_ms"
        if op_key in self.thresholds and metric.latency_ms > self.thresholds[op_key]:
            logger.warning("high_latency", operation=metric.operation, latency_ms=metric.latency_ms, engine=metric.engine)

        err_rate = self._calculate_rate(lambda m: not m.success)
        if err_rate > self.thresholds["error_rate_percent"]:
            logger.error("high_error_rate", error_rate_percent=err_rate)

        fb_rate = self._calculate_rate(lambda m: m.fallback_used)
        if fb_rate > self.thresholds["fallback_rate_percent"]:
            logger.warning("high_fallback_rate", fallback_rate_percent=fb_rate)

    def _calculate_rate(self, pred) -> float:
        window = self._window[-200:]  # sliding window
        if not window:
            return 0.0
        numer = sum(1 for m in window if pred(m))
        return (numer / len(window)) * 100.0
```

### Health Check Endpoints

```python
# health.py
from fastapi import FastAPI, Response
from typing import Dict
from datetime import datetime
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

@app.get("/health")
async def health_check() -> Dict:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "v2-llamaindex"
    }

@app.get("/health/detailed")
async def detailed_health() -> Dict:
    """Detailed health with component status"""
    return {
        "status": "healthy",
        "components": {
            "document_service": check_document_service(),
            "rag_service": check_rag_service(),
            "llm_service": check_llm_service(),
            "vector_store": check_vector_store(),
            "fallback_mechanism": check_fallback()
        },
        "metrics": {
            "avg_query_latency_ms": calculate_avg_latency(),
            "error_rate_percent": calculate_error_rate(),
            "fallback_rate_percent": calculate_fallback_rate(),
            "documents_indexed": count_indexed_documents()
        }
    }

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### Health Check Endpoints

```python
# health.py
from fastapi import FastAPI
from typing import Dict

app = FastAPI()

@app.get("/health")
async def health_check() -> Dict:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "v2-llamaindex"
    }

@app.get("/health/detailed")
async def detailed_health() -> Dict:
    """Detailed health with component status"""
    return {
        "status": "healthy",
        "components": {
            "document_service": check_document_service(),
            "rag_service": check_rag_service(),
            "llm_service": check_llm_service(),
            "vector_store": check_vector_store(),
            "fallback_mechanism": check_fallback()
        },
        "metrics": {
            "avg_query_latency_ms": calculate_avg_latency(),
            "error_rate_percent": calculate_error_rate(),
            "fallback_rate_percent": calculate_fallback_rate(),
            "documents_indexed": count_indexed_documents()
        }
    }

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint"""
    return Response(
        content=generate_prometheus_metrics(),
        media_type="text/plain"
    )
```

---

## 📈 Dashboards

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Caliper LlamaIndex Migration",
    "panels": [
      {
        "title": "Query Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(caliper_query_duration_seconds_bucket{engine='v1'}[5m])) by (le))",
            "legendFormat": "v1 p95"
          },
          {
            "expr": "histogram_quantile(0.95, sum(rate(caliper_query_duration_seconds_bucket{engine='llamaindex'}[5m])) by (le))",
            "legendFormat": "v2 p95"
          }
        ]
      },
      {
        "title": "Engine Usage",
        "targets": [{
          "expr": "sum by (engine) (rate(caliper_queries_total[5m]))"
        }]
      },
      {
        "title": "Fallback Rate %",
        "targets": [{
          "expr": "rate(caliper_fallbacks_total[5m]) / rate(caliper_queries_total{engine='llamaindex'}[5m]) * 100"
        }]
      },
      {
        "title": "Error Rate by Engine",
        "targets": [{
          "expr": "sum by (engine) (rate(caliper_errors_total[5m]))"
        }]
      },
      {
        "title": "Retrieval Accuracy & Faithfulness",
        "targets": [
          { "expr": "caliper_retrieval_accuracy", "legendFormat": "retrieval_acc" },
          { "expr": "caliper_eval_faithfulness", "legendFormat": "faithfulness" }
        ]
      }
    ]
  }
}
```

### Real-time Monitoring Script

```python
# monitor.py
#!/usr/bin/env python3
import curses
import time
from collections import deque
from prometheus_client import REGISTRY
from prometheus_client import exposition

class LiveMonitor:
    def __init__(self):
        self.v1_latencies = deque(maxlen=100)
        self.v2_latencies = deque(maxlen=100)
        self.fallback_count = 0
        self.error_count = 0

    def run(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

        while True:
            self._scrape_prom_metrics()
            stdscr.clear()
            self._draw_header(stdscr)
            self._draw_metrics(stdscr)
            self._draw_alerts(stdscr)
            stdscr.refresh()
            time.sleep(1)
            if stdscr.getch() == ord('q'):
                break

    def _scrape_prom_metrics(self):
        # Updates the deques using current metrics snapshot
        pass  # Implement as needed for local scrape

    def _draw_header(self, stdscr):
        stdscr.addstr(0, 0, "Caliper LlamaIndex Live Monitor (press 'q' to quit)")

    def _draw_metrics(self, stdscr):
        y = 2
        stdscr.addstr(y, 0, "═" * 80); y += 1
        v1_avg = sum(self.v1_latencies) / len(self.v1_latencies) if self.v1_latencies else 0
        v2_avg = sum(self.v2_latencies) / len(self.v2_latencies) if self.v2_latencies else 0
        stdscr.addstr(y, 0, "Average Latency:"); stdscr.addstr(y, 20, f"v1: {v1_avg:.2f}ms"); stdscr.addstr(y, 40, f"v2: {v2_avg:.2f}ms")
        if v2_avg > 0 and v1_avg > 0:
            improvement = ((v1_avg - v2_avg) / v1_avg) * 100
            color = curses.color_pair(1) if improvement > 0 else curses.color_pair(2)
            stdscr.addstr(y, 60, f"{improvement:+.1f}%", color)

    def _draw_alerts(self, stdscr):
        pass

if __name__ == "__main__":
    monitor = LiveMonitor()
    curses.wrapper(monitor.run)
```

---

## 🚨 Alerting Rules

### Prometheus Alert Configuration

```yaml
# alerts.yml
groups:
  - name: llamaindex_migration
    interval: 30s
    rules:
      - alert: HighFallbackRate
        expr: |
          rate(caliper_fallbacks_total[5m]) / rate(caliper_queries_total{engine='llamaindex'}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High fallback rate detected"
          description: "Fallback rate is {{ $value | humanizePercentage }} (threshold: 5%)"
      - alert: V2PerformanceDegradation
        expr: |
          histogram_quantile(0.95, sum(rate(caliper_query_duration_seconds_bucket{engine='llamaindex'}[5m])) by (le)) >
          histogram_quantile(0.95, sum(rate(caliper_query_duration_seconds_bucket{engine='v1'}[5m])) by (le)) * 1.2
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "V2 performance worse than V1"
          description: "V2 is {{ $value }}x slower than V1"
      - alert: HighErrorRate
        expr: |
          sum(rate(caliper_errors_total[5m])) / sum(rate(caliper_queries_total[5m])) > 0.02
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "Error rate is {{ $value | humanizePercentage }}"
      - alert: EvalScoreDrop
        expr: |
          (avg_over_time(caliper_eval_faithfulness[1h]) < (avg_over_time(caliper_eval_faithfulness[24h]) * 0.9))
          or (avg_over_time(caliper_retrieval_accuracy[1h]) < (avg_over_time(caliper_retrieval_accuracy[24h]) * 0.9))
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Evaluation scores dropped by >10%"
          description: "Faithfulness or retrieval accuracy degraded >10% vs 24h baseline"
```

---

## 📱 Notification Integration

### Slack Notifications

```python
# notifications.py
import requests
from typing import Dict

class NotificationService:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_migration_update(self, phase: str, status: str, metrics: Dict):
        """Send migration progress update (structured)"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"LlamaIndex Migration: Phase {phase}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Status:* {status}"},
                    {"type": "mrkdwn", "text": f"*Engine:* {metrics.get('primary_engine', 'v1')}"},
                    {"type": "mrkdwn", "text": f"*V2 Queries:* {metrics.get('v2_query_count', 0)}"},
                    {"type": "mrkdwn", "text": f"*Fallbacks:* {metrics.get('fallback_count', 0)}"},
                    {"type": "mrkdwn", "text": f"*Avg p95 Latency:* {metrics.get('p95_latency_ms', 0)}ms"},
                    {"type": "mrkdwn", "text": f"*Error Rate:* {metrics.get('error_rate', 0)}%"},
                    {"type": "mrkdwn", "text": f"*Retrieval Acc:* {metrics.get('retrieval_acc', 0):.2f}"},
                    {"type": "mrkdwn", "text": f"*Faithfulness:* {metrics.get('faithfulness', 0):.2f}"}
                ]
            }
        ]
        if status == "alert":
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"⚠️ *Alert:* {metrics.get('alert_message', 'Unknown issue')}"}
            })
        requests.post(self.webhook_url, json={"blocks": blocks})
```

---

## 📝 Logging Strategy

Use Loguru (Caliper standard). Enrich logs with migration context; avoid print().

```python
# logging_config.py
from loguru import logger
from caliper.core.config import settings

def configure_logging():
    # Configure sinks/rotation if needed; in Docker write to /app/logs
    logger.add(settings.log_path, rotation="10 MB", retention="7 days", serialize=True)

def log_query_processed(query_id: str, duration_ms: int, engine: str, fallback_used: bool, chunk_count: int, eval_scores=None):
    logger.bind(
        engine=engine,
        migration_phase=get_migration_phase(),
        build_version=get_build_version(),
    ).info(
        "query_processed",
        query_id=query_id,
        duration_ms=duration_ms,
        fallback_used=fallback_used,
        chunk_count=chunk_count,
        eval_scores=eval_scores or {},
    )
```

---

## 🔍 Debugging Tools

### Migration Debug CLI

```python
# debug_cli.py
import time
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def compare_engines(query: str):
    """Run query on both engines and compare"""
    console.print("[bold]Running comparison...[/bold]")

    v1_start = time.time(); v1_result = run_v1_query(query); v1_time = time.time() - v1_start
    v2_start = time.time(); v2_result = run_v2_query(query); v2_time = time.time() - v2_start

    table = Table(title="Engine Comparison")
    table.add_column("Metric", style="cyan")
    table.add_column("V1", style="magenta")
    table.add_column("V2 (LlamaIndex)", style="green")
    table.add_row("Response Time", f"{v1_time:.2f}s", f"{v2_time:.2f}s")
    table.add_row("Token Count", str(len(getattr(v1_result, "text", str(v1_result)).split())), str(len(getattr(v2_result, "text", str(v2_result)).split())))
    table.add_row("Sources Used", str(len(v1_result.sources)), str(len(v2_result.sources)))
    table.add_row("Similarity Score", "-", f"{calculate_similarity(v1_result, v2_result):.2%}")
    console.print(table)

@app.command()
def trace_query(query: str, engine: str = "llamaindex"):
    """Trace query execution with detailed timing"""
    tracer = QueryTracer()
    tracer.trace(query, engine)
    tracer.display_trace()

if __name__ == "__main__":
    app()
```

---

## 📊 Migration Progress Tracking

```python
# progress_tracker.py
class MigrationProgress:
    def __init__(self):
        self.checkpoints = {
            "phase_1_complete": False,
            "v2_services_deployed": False,
            "cli_integration_complete": False,
            "fallback_validated": False,
            "performance_validated": False,
            "user_acceptance_complete": False,
            "v2_as_default": False,
            "v1_deprecated": False
        }

    def update_checkpoint(self, checkpoint: str):
        self.checkpoints[checkpoint] = True
        self._notify_progress()

    def get_completion_percentage(self) -> float:
        completed = sum(1 for v in self.checkpoints.values() if v)
        return (completed / len(self.checkpoints)) * 100

    def generate_report(self) -> str:
        """Generate migration progress report"""
        return f"""
        Migration Progress: {self.get_completion_percentage():.1f}%
        ✓ Completed: {sum(1 for v in self.checkpoints.values() if v)}
        ⧖ In Progress: {sum(1 for v in self.checkpoints.values() if not v)}
        Next Milestone: {self._get_next_milestone()}
        Estimated Completion: {self._estimate_completion_date()}
        """
```

This monitoring setup ensures complete visibility into the migration process and enables quick response to any issues.
