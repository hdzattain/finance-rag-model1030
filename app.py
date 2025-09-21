"""Flask API exposing the layered quant research platform."""
from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd
from flask import Flask, jsonify, request

from quant_platform import (
    ArchitectureOptimiser,
    AgenticRAGPipeline,
    DataIngestionManager,
    FrontendArchitecturePlanner,
    HardwareAdapter,
    PlatformConfig,
    QuantBacktestManager,
    ResearchCoordinator,
    VirtualLoginSandbox,
    create_client,
)
from quant_platform.agents import DEFAULT_AGENT_REGISTRY
from quant_platform.llm import DummyLLMClient

app = Flask(__name__)

config = PlatformConfig()
provider = os.getenv("LLM_PROVIDER", "openai")
token = getattr(config.llm_tokens, provider, None)
try:
    llm_client = create_client(provider, token=token)
    # If token missing the concrete client will raise when invoked.
    # Replace with dummy proactively to keep API responsive.
    if not token:
        llm_client = DummyLLMClient(token=None)
except Exception:  # pragma: no cover - fallback path
    llm_client = DummyLLMClient(token=None)

rag_pipeline = AgenticRAGPipeline(config=config, llm_client=llm_client)
ingestion_manager = DataIngestionManager(config=config.data_sources, sink=rag_pipeline)
backtest_manager = QuantBacktestManager(platform_config=config.backtest)
research_coordinator = ResearchCoordinator()
frontend_planner = FrontendArchitecturePlanner()
virtual_sandbox = VirtualLoginSandbox()
architecture_optimiser = ArchitectureOptimiser(frameworks=["FastAPI", "Ray", "Airflow"])
hardware_adapter = HardwareAdapter(profile=config.hardware)


@app.route("/recommend", methods=["POST"])
def recommend() -> Any:
    payload = request.get_json(force=True)
    query = payload.get("query", "")
    rounds = int(payload.get("rounds", 2))
    top_k = int(payload.get("top_k", 5))
    result = rag_pipeline.run(query=query, rounds=rounds, top_k=top_k)
    return jsonify(result)


@app.route("/ingest", methods=["POST"])
def ingest() -> Any:
    payload = request.get_json(force=True)
    snowball = payload.get("snowball", [])
    indices = payload.get("indices", [])
    topics = payload.get("topics", [])
    ingestion_manager.ingest_all(snowball, indices, topics)
    return jsonify({"status": "ok"})


@app.route("/backtest/local", methods=["POST"])
def backtest_local() -> Any:
    payload = request.get_json(force=True)
    market_data = pd.DataFrame(payload.get("market_data", []))
    result = backtest_manager.backtest_local(market_data)
    return jsonify(result)


@app.route("/backtest/remote", methods=["POST"])
def backtest_remote() -> Any:
    payload = request.get_json(force=True)
    platform = payload["platform"]
    strategy_code = payload["strategy_code"]
    params = payload.get("params", {})
    result = backtest_manager.submit_remote(platform, strategy_code, params)
    return jsonify(result)


@app.route("/research", methods=["POST"])
def research() -> Any:
    payload = request.get_json(force=True)
    query = payload.get("query", "")
    human_notes = payload.get("human_notes", [])
    for note in human_notes:
        research_coordinator.add_human_insight(note)
    report = research_coordinator.compile_report(query)
    return jsonify(report)


@app.route("/frontend/login-blueprint", methods=["GET"])
def frontend_blueprint() -> Any:
    blueprint = frontend_planner.login_page_blueprint()
    serialised = {
        section: [module.__dict__ for module in modules]
        for section, modules in blueprint.items()
    }
    return jsonify(serialised)


@app.route("/agents", methods=["GET"])
def list_agents() -> Any:
    return jsonify(DEFAULT_AGENT_REGISTRY.list_agents())


@app.route("/virtual/tasks", methods=["GET", "POST", "PUT"])
def virtual_tasks() -> Any:
    if request.method == "POST":
        payload = request.get_json(force=True)
        virtual_sandbox.enqueue(payload["url"], payload.get("instructions", ""))
        return jsonify({"status": "queued"})
    if request.method == "PUT":
        payload = request.get_json(force=True)
        virtual_sandbox.mark_completed(payload["url"])
        return jsonify({"status": "completed"})
    return jsonify(virtual_sandbox.list_pending())


@app.route("/architecture/reflect", methods=["POST"])
def architecture_reflect() -> Any:
    payload = request.get_json(force=True)
    goals = payload.get("goals", [])
    reflection = architecture_optimiser.run_reflection(goals)
    return jsonify(reflection.__dict__)


@app.route("/hardware/profile", methods=["GET"])
def hardware_profile() -> Any:
    return jsonify(hardware_adapter.summary())


@app.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
