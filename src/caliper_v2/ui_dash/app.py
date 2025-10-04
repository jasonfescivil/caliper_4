from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import dash
from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc

# Load environment early
try:
    from caliper_v2.core.env import load_env

    load_env()
except Exception:
    pass

# Optional settings import (don’t fail if missing)
try:
    from caliper_v2.core.config import settings  # type: ignore
except Exception:
    settings = None  # type: ignore

# Business entrypoints (pure wrapper usage only)
from caliper_v2.services.judge_components import windows_retrieve_command, windows_retrieve_argv
from caliper_v2.commands import enhance as enhance_cmd
from caliper_v2.commands import review as review_cmd
from caliper_v2.services.ui_api import synthesize_from_context, resolve_llm_from_env_settings


# --------------------
# Helpers
# --------------------

def _normalize_provider_model(provider: Optional[str], model: Optional[str]) -> Tuple[Optional[str], Optional[str], List[Any]]:
    """
    Normalize provider/model pairs to reduce user friction.
    - If OpenAI and user enters an unknown alias like "gpt-5*", map to a safer default (gpt-4o).
    - If model is empty, leave as None so backend chooses defaults from env/settings.
    Returns: (provider, normalized_model, list_of_alerts)
    """
    alerts: List[Any] = []
    if not provider:
        return None, (model or None), alerts
    prov = (provider or "").strip()
    mdl = (model or "").strip() or None

    try:
        low = prov.lower()
        if low == "openai":
            if mdl:
                m = mdl.lower()
                # Do not remap user-specified gpt-5; honor exact request and only warn.
                if m.startswith("gpt-5") or m in {"gpt5", "gpt-5"}:
                    alerts.append(dbc.Alert("Attempting to use OpenAI 'gpt-5*'. If your project lacks access, choose a supported model or leave blank for provider default.", color="info"))
                elif m in {"gpt4", "gpt-4"}:
                    mdl = "gpt-4o"
                    alerts.append(dbc.Alert("Mapped 'gpt-4' to 'gpt-4o' (current general model).", color="info"))
        elif low == "cohere":
            # Provide frontier model default if left blank
            if not mdl:
                mdl = "command-a-reasoning-08-2025"
        elif low == "anthropic":
            # Use frontier Claude models by default
            if not mdl:
                mdl = "claude-opus-4-1-20250805"
        elif low == "gemini":
            # Use frontier Gemini model by default
            if not mdl:
                mdl = "gemini-2.5-pro-preview"
        elif low in {"xai", "grok"}:
            # Use frontier Grok models by default
            if not mdl:
                mdl = "grok-4-fast-reasoning"
    except Exception:
        # Best-effort normalization only
        pass

    return prov, mdl, alerts

def _ensure_dir(p: Path) -> Path:
    # Only create directory if it's not the current directory
    if p.resolve() != Path(".").resolve():
        p.mkdir(parents=True, exist_ok=True)
    return p


def _default_paths() -> Dict[str, Path]:
    data_dir = Path(getattr(settings, "data_dir", Path("data_v2"))).resolve()
    outputs_dir = Path(getattr(settings, "output_dir", Path("outputs"))).resolve()
    ctx_dir = _ensure_dir(data_dir / "context")
    reviews_dir = _ensure_dir(outputs_dir / "reviews")
    drafts_dir = _ensure_dir(outputs_dir / "drafts")
    return {
        "data_dir": data_dir,
        "outputs_dir": outputs_dir,
        "ctx_dir": ctx_dir,
        "reviews_dir": reviews_dir,
        "drafts_dir": drafts_dir,
    }


def _clean_path_str(s: Optional[str]) -> str:
    if not s:
        return ""
    t = s.strip()
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1].strip()
    return t


def _preview_nodes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes = (data.get("retrieval") or {}).get("nodes") or data.get("nodes") or data.get("results") or []
    rows: List[Dict[str, Any]] = []
    for n in nodes[:40]:
        md = n.get("metadata") or n.get("node", {}).get("metadata") or {}
        file = md.get("file_name") or md.get("file_path") or md.get("file") or md.get("source")
        page = md.get("page_label", md.get("page"))
        section = md.get("section") or md.get("header") or md.get("heading") or md.get("title")
        score = n.get("score") or n.get("similarity") or md.get("score")
        rows.append({"file": file, "page": page, "section": section, "score": score})
    return rows


# --------------------
# App
# --------------------

base_paths = _default_paths()

# Use a modern dark theme and include Font Awesome for icons
app: Dash = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,  # Dark theme by default for everyone
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css",  # Font Awesome for existing icon classes
    ],
    suppress_callback_exceptions=True,
)
app.title = "Caliper v2 – Dash UI"

# Stores for cross-tab state
stores = html.Div([
    dcc.Store(id="store-provider"),
    dcc.Store(id="store-model"),
    dcc.Store(id="store-retrieval-path"),
    dcc.Store(id="store-graph-path"),
    dcc.Store(id="store-enhanced-path"),
    dcc.Store(id="store-draft-path"),
    dcc.Store(id="store-review-json-path"),
    dcc.Store(id="store-review-md-path"),
])

# Provider/model controls
provider_options = [
    {"label": "Cohere", "value": "cohere"},
    {"label": "OpenAI", "value": "openai"},
    {"label": "Anthropic", "value": "anthropic"},
    {"label": "Gemini", "value": "gemini"},
    {"label": "xAI", "value": "xai"},
    {"label": "Grok (xAI)", "value": "grok"},
]
model_hints = {
    "cohere": "command-r-plus",  # Stable model for retrieval
    "openai": "gpt-5",  # Frontier model
    "anthropic": "claude-sonnet-4-5",  # Default to Sonnet for balance
    "gemini": "gemini-2.5-pro",  # Frontier model
    "xai": "grok-4",  # Frontier model
    "grok": "grok-4",  # Frontier model
}

# Provider descriptions for UI help
provider_descriptions = {
    "cohere": "Best for retrieval (embeddings + reranking). Use Command R+ for generation.",
    "openai": "Fast, reliable. GPT-5 is frontier model. Good for quick drafts.",
    "anthropic": "Excellent for engineering reports. Sonnet 4.5 (fast), Opus 4.1 (highest quality).",
    "gemini": "Long context support. Gemini 2.5 Pro for large documents.",
    "xai": "Grok-4 for fast iteration and exploration.",
}

# Note: The Cohere Generate API is deprecated; backend uses the Chat API via LlamaIndex

provider_panel = dbc.Card(
    dbc.CardBody([
        html.H5("Run profile & provider"),
        dbc.Row([
            dbc.Col(dbc.Select(id="inp-provider", options=provider_options, value="cohere"), md=3),
            dbc.Col(dbc.Input(id="inp-model", placeholder="Model (optional)", value=model_hints.get("cohere", "")), md=3),
            dbc.Col(dbc.Button("Apply", id="btn-apply-provider", color="primary"), md=2),
            dbc.Col(dbc.Button("Self-test Cohere", id="btn-provider-selftest", color="secondary", outline=True), md=2),
            dbc.Col(dbc.Button("Doctor", id="btn-doctor", color="info", outline=True), md=2),
        ], className="g-2"),
        html.Div(id="provider-status", className="mt-2", style={"fontSize": "0.9rem"}),
    ]), className="mb-3"
)

# Tabs
retrieval_tab = dcc.Tab(label="🔎 Retrieval", value="tab-retrieval")
enhance_tab = dcc.Tab(label="✨ Enhance", value="tab-enhance")
draft_tab = dcc.Tab(label="✍️ Draft", value="tab-draft")
generate_tab = dcc.Tab(label="🧪 Generate", value="tab-generate")
review_tab = dcc.Tab(label="⚖️ Judge & Review", value="tab-review")

# Retrieval content
retrieval_content = html.Div([
    dbc.Card([
        dbc.CardHeader(html.H5(["🔎 Query Input"], className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Question/Prompt", html_for="ret-question", className="fw-bold"),
                    dbc.Textarea(id="ret-question", placeholder="Enter your question for retrieval...", style={"height": 120}),
                ], md=8),
                dbc.Col([
                    dbc.Label("Or Load from File", className="fw-bold"),
                    dbc.Input(id="ret-prompt-file", placeholder="Path to prompt file", className="mb-2"),
                    dbc.Button("Load File", id="btn-load-prompt", color="secondary", size="sm", className="w-100"),
                ], md=4),
            ], className="g-3"),
        ]),
    ], className="mb-3"),

    dbc.Card([
        dbc.CardHeader(html.H5(["⚙️ Retrieval Settings (Cloud Text)"], className="mb-0")),
        dbc.CardBody([
        dbc.Row([
                dbc.Col([
                    dbc.Label("Indexes", html_for="ret-indexes", className="fw-bold"),
                    dbc.Input(id="ret-indexes", value="design", placeholder="comma-separated: federal,state,design"),
                ], md=4),
                dbc.Col([
                    dbc.Label("Top-K Results", html_for="ret-topk", className="fw-bold"),
                    dbc.Input(id="ret-topk", type="number", min=1, step=1, value=40),
                ], md=2),
                dbc.Col([
                    dbc.Label("Rerank Top-N", html_for="ret-rerank-topn", className="fw-bold"),
                    dbc.Input(id="ret-rerank-topn", type="number", min=0, step=1, value=20),
                ], md=3),
                dbc.Col([
                    dbc.Label("Output Path", html_for="ret-out", className="fw-bold"),
                    dbc.Input(id="ret-out", value=str((base_paths["ctx_dir"] / "context_000000.json").resolve())),
                ], md=3),
            ], className="g-3"),
            # Advanced retrieval controls
            dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Retrieval Mode", html_for="ret-mode", className="fw-bold"),
                            dbc.Select(id="ret-mode", options=[
                                {"label": "chunks", "value": "chunks"},
                                {"label": "files_via_content", "value": "files_via_content"},
                                {"label": "files_via_metadata", "value": "files_via_metadata"},
                                {"label": "auto_routed", "value": "auto_routed"},
                            ], value=None),
                        ], md=3),
                        dbc.Col([
                            dbc.Label("Dense K", html_for="ret-densek", className="fw-bold"),
                            dbc.Input(id="ret-densek", type="number", min=0, step=1, placeholder="e.g., 12"),
                        ], md=2),
                        dbc.Col([
                            dbc.Label("Sparse K", html_for="ret-sparsesk", className="fw-bold"),
                            dbc.Input(id="ret-sparsek", type="number", min=0, step=1, placeholder="e.g., 12"),
                        ], md=2),
                        dbc.Col([
                            dbc.Label("Alpha", html_for="ret-alpha", className="fw-bold"),
                            dbc.Input(id="ret-alpha", type="number", step=0.05, min=0, max=1, placeholder="0.5"),
                        ], md=2),
                        dbc.Col([
                            dbc.Label("Expand Queries", html_for="ret-expand", className="fw-bold"),
                            dbc.Input(id="ret-expand", type="number", min=0, step=1, placeholder="e.g., 4"),
                        ], md=3),
                    ], className="g-3 mb-2"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Include Terms", html_for="ret-include-terms", className="fw-bold"),
                            dbc.Input(id="ret-include-terms", placeholder="comma,separated,terms"),
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Exclude Sections", html_for="ret-exclude-sections", className="fw-bold"),
                            dbc.Input(id="ret-exclude-sections", placeholder="toc,glossary,references,figures"),
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Filters (JSON)", html_for="ret-filters", className="fw-bold"),
                            dbc.Input(id="ret-filters", placeholder='{"jurisdiction":"WA","chapter":"G1"}'),
                        ], md=4),
                    ], className="g-3 mb-2"),
                    dbc.Row([
                        dbc.Col(dbc.Checklist(options=[{"label": "Infer Filters", "value": "infer"}], value=[], id="ret-infer"), md=3),
                        dbc.Col(dbc.Checklist(options=[{"label": "HyDE", "value": "hyde"}], value=[], id="ret-hyde"), md=3),
                    ], className="g-3"),
                ], title="Advanced Retrieval"),
            ], start_collapsed=True),
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-search me-2"), 
                        "Run Retrieval"
                    ], id="btn-retrieve", color="primary", size="lg", className="w-100 mt-3"),
                ]),
            ]),
        ]),
    ], className="mb-3"),

    dbc.Accordion([
        dbc.AccordionItem([
            dcc.Textarea(id="ret-command", style={"width": "100%", "height": 80, "fontFamily": "monospace", "fontSize": "0.85rem"}),
        ], title="🔧 Generated Command", item_id="cmd"),
        dbc.AccordionItem([
            dcc.Textarea(id="ret-logs", style={"width": "100%", "height": 180, "fontFamily": "monospace", "fontSize": "0.85rem"}),
        ], title="📋 Execution Logs", item_id="logs"),
    ], start_collapsed=True, className="mb-3"),

    html.Div(id="ret-result", className="mt-3 mb-4"),

    # GraphRAG settings
    dbc.Card([
        dbc.CardHeader(html.H5(["🕸️ GraphRAG Retrieval (optional mix with text)"], className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Graph Dir", html_for="graph-dir", className="fw-bold"),
                    dbc.Input(id="graph-dir", value=str((base_paths["data_dir"] / "graph").resolve()), placeholder="data_v2/graph"),
                ], md=4),
                dbc.Col([
                    dbc.Label("Hops", html_for="graph-hops", className="fw-bold"),
                    dbc.Input(id="graph-hops", type="number", min=0, step=1, value=1),
                ], md=2),
                dbc.Col([
                    dbc.Label("Limit", html_for="graph-limit", className="fw-bold"),
                    dbc.Input(id="graph-limit", type="number", min=1, step=1, value=200),
                ], md=2),
                dbc.Col([
                    dbc.Label("Output Path", html_for="graph-out", className="fw-bold"),
                    dbc.Input(id="graph-out", value=str((base_paths["ctx_dir"] / "graph_ctx_000000.json").resolve())),
                ], md=4),
            ], className="g-3 mb-2"),
            dbc.Row([
                dbc.Col(dbc.Checklist(options=[{"label": "Mix with Cloud Text", "value": "mix"}], value=[], id="graph-mix"), md=3),
                dbc.Col(dbc.Input(id="graph-text-indexes", value="design", placeholder="comma-separated indexes for mixing"), md=3),
                dbc.Col(dbc.Input(id="graph-topk", type="number", min=1, step=1, value=40), md=2),
                dbc.Col(dbc.Input(id="graph-rerank", type="number", min=1, step=1, value=20), md=2),
                dbc.Col(dbc.Button([html.I(className="fas fa-project-diagram me-2"), "Run GraphRAG"], id="btn-graph", color="secondary", size="lg", className="w-100"), md=2),
            ], className="g-3"),
        ]),
    ], className="mb-3"),

    dbc.Accordion([
        dbc.AccordionItem([
            dcc.Textarea(id="ret-graph-command", style={"width": "100%", "height": 80, "fontFamily": "monospace", "fontSize": "0.85rem"}),
        ], title="🔧 GraphRAG Command", item_id="gcmd"),
        dbc.AccordionItem([
            dcc.Textarea(id="ret-graph-logs", style={"width": "100%", "height": 180, "fontFamily": "monospace", "fontSize": "0.85rem"}),
        ], title="📋 GraphRAG Logs", item_id="glogs"),
    ], start_collapsed=True, className="mb-3"),

    html.Div(id="ret-graph-result", className="mt-3"),
])

# Enhance content
enhance_content = html.Div([
    dbc.Card([
        dbc.CardHeader(html.H5(["✨ Context Enhancement"], className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Context Input Path", html_for="enh-ctx", className="fw-bold"),
                    dbc.Input(id="enh-ctx", placeholder="Path to retrieval context JSON", value=""),
                ], md=6),
                dbc.Col([
                    dbc.Label("Enhanced Output Path", html_for="enh-out", className="fw-bold"),
                    dbc.Input(id="enh-out", placeholder="Where to save enhanced context", value=str((base_paths["ctx_dir"] / "enhanced_000000.json").resolve())),
                ], md=6),
            ], className="g-3 mb-3"),
            dbc.Button([
                html.I(className="fas fa-magic me-2"),
                "Enhance Context"
            ], id="btn-enhance", color="success", size="lg", className="w-100"),
        ]),
    ], className="mb-3"),
    html.Div(id="enh-status", className="mt-3"),
])

# Draft content
draft_content = html.Div([
    dbc.Card([
        dbc.CardHeader(html.H5(["✍️ Draft Editor"], className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Draft File Path", html_for="drf-path", className="fw-bold"),
                    dbc.Input(id="drf-path", value=str((base_paths["drafts_dir"] / "draft_000000.md").resolve())),
                ], md=8),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button([html.I(className="fas fa-folder-open me-1"), "Load"], id="btn-draft-load", color="info"),
                        dbc.Button([html.I(className="fas fa-save me-1"), "Save"], id="btn-draft-save", color="success"),
                    ], className="w-100"),
                ], md=4),
            ], className="g-2 mb-3"),
            dbc.Label("Draft Content", className="fw-bold"),
            dbc.Textarea(id="drf-text", style={"height": 400, "fontFamily": "monospace"}, placeholder="Your draft content will appear here..."),
        ]),
    ], className="mb-3"),
    html.Div(id="drf-status"),
])

# Generate content
generate_content = html.Div([
    dbc.Card([
        dbc.CardHeader(html.H5(["🧪 AI Generation Settings"], className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Context Path", html_for="gen-ctx", className="fw-bold"),
                    dbc.Input(id="gen-ctx", placeholder="Path to context JSON file", value=""),
                ], md=6),
                dbc.Col([
                    dbc.Label("Generation Style", html_for="gen-style", className="fw-bold"),
                    dbc.Select(id="gen-style", options=[
                        {"label": "Strict Citation", "value": "strict-citation"},
                        {"label": "Compare", "value": "compare"},
                        {"label": "Outline", "value": "outline"},
                        {"label": "Quote Heavy", "value": "quote-heavy"},
                    ], value="strict-citation"),
                ], md=3),
                dbc.Col([
                    dbc.Label("Output Path", html_for="gen-out", className="fw-bold"),
                    dbc.Input(id="gen-out", placeholder="Generated draft location", value=str((base_paths["drafts_dir"] / "generation_000000.md").resolve())),
                ], md=3),
            ], className="g-3 mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("AI Provider", html_for="gen-provider", className="fw-bold"),
                    dbc.Select(id="gen-provider", options=provider_options, value="cohere"),
                ], md=4),
                dbc.Col([
                    dbc.Label("Model", html_for="gen-model", className="fw-bold"),
                    dbc.Input(id="gen-model", placeholder="Model name (optional)", value=model_hints.get("cohere", "")),
                ], md=4),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-robot me-2"),
                        "Generate"
                    ], id="btn-generate", color="primary", size="lg", className="w-100 mt-4"),
                ], md=4),
            ], className="g-3"),
        ]),
    ], className="mb-3"),
    dcc.Loading(id="gen-loading-status", type="default", children=html.Div(id="gen-status", className="mb-3")),
    dcc.Loading(id="gen-loading-preview", type="default", children=dbc.Card([
        dbc.CardHeader("📄 Generated Preview"),
        dbc.CardBody([
            html.Div(id="gen-preview", style={"whiteSpace": "pre-wrap", "fontFamily": "monospace", "fontSize": "0.9rem", "maxHeight": "300px", "overflowY": "auto"}),
        ]),
    ], id="gen-preview-card", style={"display": "none"})),
])

# Review content
review_content = html.Div([
    dbc.Card([
        dbc.CardHeader(html.H5(["⚖️ Review & Judgment Settings"], className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Context Path", html_for="rev-ctx", className="fw-bold"),
                    dbc.Input(id="rev-ctx", placeholder="Path to context JSON", value=""),
                ], md=6),
                dbc.Col([
                    dbc.Label("Draft Path", html_for="rev-draft", className="fw-bold"),
                    dbc.Input(id="rev-draft", placeholder="Path to draft markdown", value=""),
                ], md=6),
            ], className="g-3 mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("JSON Output", html_for="rev-json", className="fw-bold"),
                    dbc.Input(id="rev-json", value=str((base_paths["reviews_dir"] / "review_000000.json").resolve())),
                ], md=6),
                dbc.Col([
                    dbc.Label("Markdown Output", html_for="rev-md", className="fw-bold"),
                    dbc.Input(id="rev-md", value=str((base_paths["reviews_dir"] / "review_000000.md").resolve())),
                ], md=6),
            ], className="g-3 mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Review Options", className="fw-bold"),
                    dbc.Checklist(options=[{"label": "Strict Mode", "value": "strict"}], value=["strict"], id="rev-strict"),
                ], md=4),
                dbc.Col([
                    dbc.Label("Max Evidence per Claim", html_for="rev-max-ev", className="fw-bold"),
                    dbc.Input(id="rev-max-ev", type="number", min=1, step=1, value=5),
                ], md=4),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-gavel me-2"),
                        "Run Full Review"
                    ], id="btn-review", color="warning", size="lg", className="w-100 mt-4"),
                ], md=4),
            ], className="g-3"),
        ]),
    ], className="mb-3"),
    html.Div(id="rev-status", className="mb-3"),
    dbc.Card([
        dbc.CardHeader("📊 Review Summary"),
        dbc.CardBody([
            html.Div(id="rev-md-preview", style={"whiteSpace": "pre-wrap", "fontFamily": "monospace", "fontSize": "0.9rem", "maxHeight": "400px", "overflowY": "auto"}),
        ]),
    ], id="rev-preview-card", style={"display": "none"}),
])

# Auto-fill model hint based on provider selection without overwriting the field value
@app.callback(Output("gen-model", "placeholder"), Input("gen-provider", "value"))
def on_gen_provider_change_placeholder(prov: str):
    try:
        return model_hints.get((prov or "").lower(), "Model name (optional)")
    except Exception:
        return "Model name (optional)"

app.layout = dbc.Container([
    html.H2("Caliper v2 – Dash/Plotly Wrapper"),
    provider_panel,
    stores,
    dcc.Tabs(id="tabs", value="tab-retrieval", children=[
        retrieval_tab, enhance_tab, draft_tab, generate_tab, review_tab
    ]),
    html.Div(id="tab-content", className="mt-3"),
], fluid=True)

# Tell Dash about all components used by callbacks, even if not rendered yet (tabs)
app.validation_layout = html.Div([
    dbc.Container([
        html.H2("Caliper v2 – Dash/Plotly Wrapper"),
        provider_panel,
        stores,
        dcc.Tabs(id="tabs", value="tab-retrieval", children=[
            retrieval_tab, enhance_tab, draft_tab, generate_tab, review_tab
        ]),
        html.Div(id="tab-content", className="mt-3"),
    ], fluid=True),
    # Include every tab’s content so their IDs are discoverable for validation
    retrieval_content,
    enhance_content,
    draft_content,
    generate_content,
    review_content,
])


# --------------------
# Callbacks – Tab content
# --------------------

@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab_id: str):
    if tab_id == "tab-retrieval":
        return retrieval_content
    if tab_id == "tab-enhance":
        return enhance_content
    if tab_id == "tab-draft":
        return draft_content
    if tab_id == "tab-generate":
        return generate_content
    if tab_id == "tab-review":
        return review_content
    return html.Div()


# Provider apply — updates stores and status only
@app.callback(
    [Output("store-provider", "data"), Output("store-model", "data"), Output("provider-status", "children")],
    [Input("btn-apply-provider", "n_clicks"), Input("btn-provider-selftest", "n_clicks"), Input("btn-doctor", "n_clicks")],
    [State("inp-provider", "value"), State("inp-model", "value")],
    prevent_initial_call=True,
)
def on_apply_provider(apply_clicks: int, selftest_clicks: int, doctor_clicks: int, provider: str, model: str):
    status: List[Any] = []
    # Track which button triggered
    trigger_id = (ctx.triggered_id or "")

    # Persist selection for CLI retrieval even if in-process config fails
    prov_in = (provider or "").strip()
    mdl_in = (model or "").strip() or None

    prov, mdl, alerts = _normalize_provider_model(prov_in, mdl_in)
    status.extend(alerts)

    # If Doctor button clicked, run CLI doctor and display
    if trigger_id == "btn-doctor":
        try:
            import subprocess, tempfile
            argv = ["poetry", "run", "caliper_v2", "doctor"]
            res = subprocess.run(argv, shell=False, capture_output=True, text=True)
            if res.returncode == 0:
                status.append(dbc.Alert("Doctor completed successfully.", color="success"))
                # Show output in a pre block
                out_text = (res.stdout or "")
                status.append(html.Pre(out_text, style={"whiteSpace": "pre-wrap", "fontSize": "0.85rem"}))
            else:
                status.append(dbc.Alert("Doctor encountered errors. See output below.", color="danger"))
                out_text = (res.stdout or "") + ("\n" + (res.stderr or "") if res.stderr else "")
                status.append(html.Pre(out_text, style={"whiteSpace": "pre-wrap", "fontSize": "0.85rem"}))
        except Exception as exc:
            status.append(dbc.Alert(f"Doctor failed to run: {exc}", color="danger"))
        return prov, mdl, status

    # If Cohere self-test button was clicked, run a lightweight readiness check
    if trigger_id == "btn-provider-selftest":
        try:
            if prov and prov.lower() == "cohere":
                if not os.getenv("COHERE_API_KEY"):
                    status.append(dbc.Alert("COHERE_API_KEY is missing in environment/.env", color="danger"))
                else:
                    # Perform a minimal chat API call via LlamaIndex to avoid direct SDK deps
                    from caliper_v2.core.llm_providers import configure_llm_provider as _cfg
                    from llama_index.core import Settings as _Settings  # type: ignore
                    _cfg("cohere", model=mdl)
                    if getattr(_Settings, "llm", None) is None:
                        status.append(dbc.Alert("Failed to bind Cohere LLM in-process.", color="danger"))
                    else:
                        try:
                            r = _Settings.llm.complete("ping")
                            ok = bool(getattr(r, "text", str(r)))
                            if ok:
                                status.append(dbc.Alert("Cohere self-test OK (chat completion succeeded)", color="success"))
                            else:
                                status.append(dbc.Alert("Cohere self-test returned empty response", color="warning"))
                        except Exception as _exc:
                            status.append(dbc.Alert(f"Cohere self-test failed: {_exc}", color="danger"))
            else:
                status.append(dbc.Alert("Self-test currently implemented for Cohere only.", color="info"))
        except Exception as exc:
            status.append(dbc.Alert(f"Self-test error: {exc}", color="danger"))
        # Do not attempt to reconfigure again; return stores and status
        return prov, mdl, status

    # Try to configure now for generate/review paths that use LlamaIndex Settings
    try:
        if prov:
            # Credential presence warnings per provider for better UX
            missing = []
            try:
                low = prov.lower()
                if low == "openai" and not os.getenv("OPENAI_API_KEY"): missing.append("OPENAI_API_KEY")
                if low == "cohere" and not os.getenv("COHERE_API_KEY"): missing.append("COHERE_API_KEY")
                if low in {"xai", "grok"} and not os.getenv("XAI_API_KEY"): missing.append("XAI_API_KEY")
                if low == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"): missing.append("ANTHROPIC_API_KEY")
                if low == "gemini" and not (
                    os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                ):
                    missing.append("GEMINI_API_KEY/GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS")
            except Exception:
                pass
            if missing:
                status.append(dbc.Alert(f"Missing credentials for {prov}: {', '.join(missing)}", color="warning"))
            # Lazy import to avoid heavy LlamaIndex import at app startup
            try:
                from caliper_v2.core.llm_providers import configure_llm_provider as _cfg
                _cfg(prov, model=mdl)
                status.append(dbc.Alert(f"Configured provider: {prov} ({mdl or 'default'})", color="success"))
            except Exception as _exc:
                status.append(dbc.Alert(f"Provider configuration failed in-process, but CLI flags will still be applied: {_exc}", color="warning"))
        else:
            status.append(dbc.Alert("Select a provider before applying.", color="secondary"))
    except Exception as exc:
        status.append(dbc.Alert(f"Provider configuration encountered an error: {exc}", color="warning"))
    # Return only store updates and status; a separate callback syncs the Generate controls when that tab is active
    return prov, mdl, status

# Sync Generate tab controls when entering the tab or when store changes
@app.callback(
    [Output("gen-provider", "value"), Output("gen-model", "value")],
    [Input("tabs", "value"), Input("store-provider", "data"), Input("store-model", "data")],
    prevent_initial_call=True,
)
def sync_generate_controls(tab_value: str, prov: Optional[str], mdl: Optional[str]):
    if tab_value != "tab-generate":
        raise dash.exceptions.PreventUpdate
    return (prov or "cohere"), (mdl or model_hints.get((prov or "cohere").lower(), ""))


# Load prompt from file
@app.callback(
    Output("ret-question", "value"),
    Input("btn-load-prompt", "n_clicks"),
    State("ret-prompt-file", "value"),
    prevent_initial_call=True,
)
def load_prompt_file(n_clicks: int, file_path: str):
    if not file_path:
        return dash.no_update
    try:
        path = Path(_clean_path_str(file_path))
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="ignore")
            return content
        else:
            return dash.no_update
    except Exception:
        return dash.no_update

# Retrieval run (cloud text)
@app.callback(
    [Output("ret-command", "value"), Output("ret-logs", "value"), Output("ret-result", "children"), Output("store-retrieval-path", "data"), Output("ret-out", "value")],
    [Input("btn-retrieve", "n_clicks")],
    [
        State("ret-question", "value"),
        State("ret-indexes", "value"),
        State("ret-topk", "value"),
        State("ret-rerank-topn", "value"),
        State("ret-out", "value"),
        State("store-provider", "data"),
        State("store-model", "data"),
        # Advanced states
        State("ret-mode", "value"),
        State("ret-densek", "value"),
        State("ret-sparsek", "value"),
        State("ret-alpha", "value"),
        State("ret-include-terms", "value"),
        State("ret-exclude-sections", "value"),
        State("ret-filters", "value"),
        State("ret-infer", "value"),
        State("ret-expand", "value"),
        State("ret-hyde", "value"),
    ],
    prevent_initial_call=True,
)
def on_retrieve(n_clicks: int, question: str, indexes_text: str, topk: int, rerank_topn: int, out_path: str, prov: Optional[str], mdl: Optional[str],
                mode: Optional[str], densek: Optional[int], sparsek: Optional[int], alpha: Optional[float], include_terms: Optional[str], exclude_sections: Optional[str],
                filters: Optional[str], infer_vals: List[str], expand: Optional[int], hyde_vals: List[str]):
    question = (question or "").strip()
    if not question:
        return "", "", dbc.Alert("Please enter a question.", color="warning"), None, out_path
    idxs = [s.strip() for s in (indexes_text or "").split(",") if s.strip()]
    out_clean = _clean_path_str(out_path or "")
    infer_filters = bool(infer_vals and "infer" in infer_vals)
    hyde = True if (hyde_vals and "hyde" in hyde_vals) else False
    cmd = windows_retrieve_command(
        question, idxs, out_clean, int(topk or 40), int(rerank_topn or 20), prov, mdl,
        retrieval_mode=mode, dense_k=densek, sparse_k=sparsek, alpha=alpha,
        include_terms=(include_terms or ""), exclude_sections=(exclude_sections or ""),
        filters=(filters or ""), infer_filters=infer_filters, expand_queries=expand, hyde=hyde,
    )
    argv = windows_retrieve_argv(
        question, idxs, out_clean, int(topk or 40), int(rerank_topn or 20), prov, mdl,
        retrieval_mode=mode, dense_k=densek, sparse_k=sparsek, alpha=alpha,
        include_terms=(include_terms or ""), exclude_sections=(exclude_sections or ""),
        filters=(filters or ""), infer_filters=infer_filters, expand_queries=expand, hyde=hyde,
    )

    # Snapshot existing files to detect newly created if CLI rewrites the name
    ctx_dir = base_paths["ctx_dir"]
    try:
        before = {p.resolve() for p in Path(ctx_dir).glob("*.json")}
    except Exception:
        before = set()

    result = subprocess.run(argv, shell=False, capture_output=True, text=True)
    logs = (result.stdout or "") + ("\n" + (result.stderr or "") if result.stderr else "")

    used_path: Optional[Path] = None
    if result.returncode == 0:
        p = Path(out_clean)
        if p.exists():
            used_path = p
        else:
            try:
                after = {q.resolve() for q in Path(ctx_dir).glob("*.json")}
                new_files = list(after - before)
                if new_files:
                    used_path = max(new_files, key=lambda q: q.stat().st_mtime)
            except Exception:
                pass

    if used_path and used_path.exists():
        try:
            data = json.loads(used_path.read_text(encoding="utf-8"))
            rows = _preview_nodes(data)
            table = dbc.Table([html.Thead(html.Tr([html.Th(k) for k in ["file", "page", "section", "score"]]))] +
                              [html.Tbody([html.Tr([html.Td(r.get("file")), html.Td(r.get("page")), html.Td(r.get("section")), html.Td(r.get("score"))]) for r in rows])],
                              bordered=True, striped=True, hover=True)
        except Exception:
            table = html.Div()
        return cmd, logs, html.Div([dbc.Alert(f"Retrieval successful: {used_path}", color="success"), table]), str(used_path), str(used_path)
    else:
        return cmd, logs, dbc.Alert("Retrieval failed or output file not found. See logs above.", color="danger"), None, out_path


# GraphRAG run
@app.callback(
    [
        Output("ret-graph-command", "value"),
        Output("ret-graph-logs", "value"),
        Output("ret-graph-result", "children"),
        Output("store-graph-path", "data"),
        Output("graph-out", "value"),
    ],
    [Input("btn-graph", "n_clicks")],
    [
        State("ret-question", "value"),
        State("graph-dir", "value"),
        State("graph-hops", "value"),
        State("graph-limit", "value"),
        State("graph-out", "value"),
        State("graph-mix", "value"),
        State("graph-text-indexes", "value"),
        State("graph-topk", "value"),
        State("graph-rerank", "value"),
        State("store-provider", "data"),
        State("store-model", "data"),
    ],
    prevent_initial_call=True,
)
def on_graph_retrieve(n_clicks: int, question: str, graph_dir: str, hops: int, limit: int, out_path: str, mix_vals: List[str], text_indexes: str, top_k: int, rerank: int, prov: Optional[str], mdl: Optional[str]):
    # Debug: log inputs
    import sys
    print(f"DEBUG GraphRAG: n_clicks={n_clicks}, question='{question[:50] if question else None}...', graph_dir='{graph_dir}'")
    sys.stdout.flush()
    
    question = (question or "").strip()
    if not question:
        return "", "", dbc.Alert("Please enter a question.", color="warning"), None, out_path
    gdir = _clean_path_str(graph_dir or "")
    out_clean = _clean_path_str(out_path or "")
    
    # Debug: log cleaned paths
    print(f"DEBUG GraphRAG: gdir='{gdir}', out_clean='{out_clean}'")
    sys.stdout.flush()

    # Compose Windows-friendly command string
    mix_flag = " --mix-with-text" if (mix_vals and "mix" in mix_vals) else ""
    txt = f" --text-indexes \"{(text_indexes or '').strip()}\" --top-k {int(top_k or 40)} --rerank-top-n {int(rerank or 20)}" if mix_flag else ""
    prov_model = "";
    if prov:
        prov_model += f" --provider {prov}"
    if mdl:
        prov_model += f" --model \"{mdl}\""
    cmd = (
        f"poetry run caliper_v2 graph retrieve \"{question}\" --graph-dir \"{gdir}\" --hops {int(hops or 1)} --limit {int(limit or 200)} --out \"{out_clean}\"" + mix_flag + txt + prov_model
    )

    # Also build a Windows-safe argv list for execution
    argv: List[str] = [
        "poetry", "run", "caliper_v2", "graph", "retrieve",
        question,
        "--graph-dir", gdir,
        "--hops", str(int(hops or 1)),
        "--limit", str(int(limit or 200)),
        "--out", out_clean,
    ]
    if mix_vals and "mix" in mix_vals:
        argv.append("--mix-with-text")
        argv += ["--text-indexes", (text_indexes or "").strip(), "--top-k", str(int(top_k or 40)), "--rerank-top-n", str(int(rerank or 20))]
    if prov:
        argv += ["--provider", prov]
    if mdl:
        argv += ["--model", mdl]

    # Snapshot possible outputs
    ctx_dir = base_paths["ctx_dir"]
    try:
        before = {p.resolve() for p in Path(ctx_dir).glob("*.json")}
    except Exception:
        before = set()

    # Show command being executed
    print(f"Executing GraphRAG: {' '.join(argv[:10])}...")
    result = subprocess.run(argv, shell=False, capture_output=True, text=True)
    logs = (result.stdout or "") + ("\n" + (result.stderr or "") if result.stderr else "")
    
    # If no logs, add a status message
    if not logs.strip():
        logs = f"Command executed with return code: {result.returncode}"

    used_path: Optional[Path] = None
    # Check both return code 0 and if any new files were created
    p = Path(out_clean)
    if p.exists():
        used_path = p
    else:
        # Look for any new JSON files created during execution
        try:
            after = {q.resolve() for q in Path(ctx_dir).glob("*.json")}
            new_files = list(after - before)
            if new_files:
                used_path = max(new_files, key=lambda q: q.stat().st_mtime)
                print(f"GraphRAG output detected at: {used_path}")
        except Exception as e:
            print(f"Error checking for output files: {e}")

    if used_path and used_path.exists():
        try:
            data = json.loads(used_path.read_text(encoding="utf-8"))
            rows = _preview_nodes(data)
            table = dbc.Table([
                html.Thead(html.Tr([html.Th(k) for k in ["file", "page", "section", "score"]])),
                html.Tbody([html.Tr([html.Td(r.get("file")), html.Td(r.get("page")), html.Td(r.get("section")), html.Td(r.get("score"))]) for r in rows])
            ], bordered=True, striped=True, hover=True)
        except Exception:
            table = html.Div()
        return cmd, logs, html.Div([dbc.Alert(f"GraphRAG successful: {used_path}", color="success"), table]), str(used_path), str(used_path)
    else:
        # Provide more informative message
        if result.returncode != 0:
            msg = f"GraphRAG command failed with exit code {result.returncode}. Check logs in the accordion below."
        else:
            msg = "GraphRAG may have completed but output file not found at expected location. Check the context directory for new files."
        return cmd, logs, dbc.Alert(msg, color="warning"), None, out_path


# Enhance
@app.callback(
    [Output("enh-status", "children"), Output("store-enhanced-path", "data"), Output("enh-ctx", "value")],
    [Input("btn-enhance", "n_clicks")],
    [State("enh-ctx", "value"), State("enh-out", "value"), State("store-retrieval-path", "data")],
    prevent_initial_call=True,
)
def on_enhance(n_clicks: int, ctx_path: str, out_path: str, stored_ctx: Optional[str]):
    ctx = _clean_path_str(ctx_path or stored_ctx or "")
    if not ctx or not Path(ctx).exists():
        return dbc.Alert("Context path not found.", color="warning"), None, ctx
    out = _clean_path_str(out_path or "")
    try:
        enhance_cmd.main(in_path=str(Path(ctx)), out_path=str(Path(out)), write_outline=True, rewrite_spore=True, suggest_retrieve=True)
        return dbc.Alert(f"Enhanced context written to: {out}", color="success"), out, ctx
    except Exception as exc:
        return dbc.Alert(f"Enhance failed: {exc}", color="danger"), None, ctx


# Draft load/save
@app.callback(
    [Output("drf-text", "value"), Output("drf-status", "children"), Output("store-draft-path", "data")],
    [Input("btn-draft-load", "n_clicks"), Input("btn-draft-save", "n_clicks")],
    [State("drf-path", "value"), State("drf-text", "value")],
    prevent_initial_call=True,
)
def on_draft(load_clicks: int, save_clicks: int, path_text: str, content: str):
    trigger = (ctx.triggered_id or "")
    p = Path(_clean_path_str(path_text or ""))
    if trigger == "btn-draft-load":
        if p.exists():
            try:
                return p.read_text(encoding="utf-8", errors="ignore"), dbc.Alert(f"Loaded: {p}", color="info"), str(p)
            except Exception as exc:
                return "", dbc.Alert(f"Load failed: {exc}", color="danger"), None
        else:
            return "", dbc.Alert("File not found.", color="warning"), None
    elif trigger == "btn-draft-save":
        try:
            # Only create parent directory if it's not the current directory
            if p.parent != Path("."):
                p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content or "", encoding="utf-8")
            return content, dbc.Alert(f"Saved: {p}", color="success"), str(p)
        except Exception as exc:
            return content, dbc.Alert(f"Save failed: {exc}", color="danger"), None
    return dash.no_update, dash.no_update, dash.no_update

# Show/hide preview cards based on content
app.clientside_callback(
    """
    function(preview_text) {
        if (preview_text && preview_text.trim()) {
            return {"display": "block"};
        }
        return {"display": "none"};
    }
    """,
    Output("gen-preview-card", "style"),
    Input("gen-preview", "children")
)

app.clientside_callback(
    """
    function(preview_text) {
        if (preview_text && preview_text.trim()) {
            return {"display": "block"};
        }
        return {"display": "none"};
    }
    """,
    Output("rev-preview-card", "style"),
    Input("rev-md-preview", "children")
)



# Generate
@app.callback(
    [Output("gen-status", "children"), Output("gen-preview", "children"), Output("gen-out", "value")],
    [Input("btn-generate", "n_clicks")],
    [State("gen-ctx", "value"), State("gen-style", "value"), State("gen-provider", "value"), State("gen-model", "value"), State("gen-out", "value"), State("store-provider", "data"), State("store-model", "data")],
    prevent_initial_call=True,
)
def on_generate(n_clicks: int, ctx_path: str, style: str, provider: str, model: str, out_path: str, stored_prov: Optional[str], stored_model: Optional[str]):
    ctx = _clean_path_str(ctx_path or "")
    if not ctx or not Path(ctx).exists():
        return dbc.Alert("Context path not found.", color="warning"), "", out_path
    try:
        alerts: List[Any] = []
        # Final provider/model chosen: UI fields override the stored values when non-empty
        prov_input = (provider or stored_prov or "").strip()
        mdl_input = (model or stored_model or "").strip() or None
        if not prov_input:
            return dbc.Alert("Please select a provider (e.g., Cohere or OpenAI) and try again.", color="warning"), "", out_path

        prov, mdl, norm_alerts = _normalize_provider_model(prov_input, mdl_input)
        alerts.extend(norm_alerts)

        # Configure provider for this run
        try:
            # Lazy import to avoid heavy LlamaIndex import at app startup
            try:
                from caliper_v2.core.llm_providers import configure_llm_provider as _cfg
                _cfg(prov, model=mdl)
            except Exception as conf_exc:
                # Surface configuration failure without crashing
                alerts.append(dbc.Alert(f"Provider configuration failed in-process: {conf_exc}", color="warning"))
                # Proceed without configure (backend callable may resolve from env)
        except Exception:
            pass
        text = synthesize_from_context(context_path=str(Path(ctx)), style=style, llm_provider=prov, llm_model=mdl)
        out = Path(_clean_path_str(out_path or ""))
        # Only create parent directory if it's not the current directory
        if out.parent != Path("."):
            out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        alerts.append(dbc.Alert(f"Generation complete and saved to: {out}", color="success"))
        return alerts, text[:500] + ("..." if len(text) > 500 else ""), str(out)
    except Exception as exc:
        return dbc.Alert(f"Generation failed: {exc}", color="danger"), "", out_path


# Review
@app.callback(
    [Output("rev-status", "children"), Output("rev-md-preview", "children"), Output("store-review-json-path", "data"), Output("store-review-md-path", "data")],
    [Input("btn-review", "n_clicks")],
    [State("rev-ctx", "value"), State("rev-draft", "value"), State("rev-json", "value"), State("rev-md", "value"), State("rev-strict", "value"), State("rev-max-ev", "value")],
    prevent_initial_call=True,
)
def on_review(n_clicks: int, ctx_path: str, draft_path: str, out_json: str, out_md: str, strict_vals: List[str], max_ev: int):
    # Debug: Check if this callback should actually run
    if not n_clicks or n_clicks < 1:
        # Return empty state if button hasn't been clicked
        return "", "", None, None
    
    ctx = _clean_path_str(ctx_path or ""); drf = _clean_path_str(draft_path or "")
    if not Path(ctx).exists() or not Path(drf).exists():
        return dbc.Alert("Context or Draft path not found.", color="warning"), "", None, None
    outj = Path(_clean_path_str(out_json or "")); outm = Path(_clean_path_str(out_md or ""))
    try:
        res = review_cmd.main(context_path=str(Path(ctx)), draft_path=str(Path(drf)), out_json=str(outj), out_md=str(outm), strict=("strict" in (strict_vals or [])), max_evidence_per_claim=int(max_ev or 5))
        md_text = Path(res.get("md", outm)).read_text(encoding="utf-8", errors="ignore")
        return dbc.Alert("Review complete.", color="success"), md_text, str(res.get("json", outj)), str(res.get("md", outm))
    except Exception as exc:
        return dbc.Alert(f"Review failed: {exc}", color="danger"), "", None, None


# Prefill provider/model if resolvable from env/settings on app start (client-side state will be empty until Apply is clicked)
@app.callback(
    [Output("inp-provider", "value"), Output("inp-model", "value")],
    Input("tabs", "value"),
    prevent_initial_call=False,
)
def on_app_mount(tab_value: str):
    try:
        p, m, src = resolve_llm_from_env_settings()
        if p or m:
            # Prefill controls only; the status message is shown after clicking Apply
            return p or dash.no_update, (m or model_hints.get(p or "cohere", ""))
    except Exception:
        pass
    return dash.no_update, dash.no_update


if __name__ == "__main__":
    # Run the Dash development server (Dash 3: app.run; Dash 2: app.run_server)
    run = getattr(app, "run", None)
    if callable(run):
        app.run(debug=True)
    else:
        app.run_server(debug=True)
