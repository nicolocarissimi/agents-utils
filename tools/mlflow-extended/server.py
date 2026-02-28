#!/usr/bin/env python3
"""Standalone MLflow MCP server for querying runs, metrics, and artifacts."""

import os
from typing import Optional

from fastmcp import FastMCP
from mlflow import MlflowClient

DEFAULT_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")

mcp = FastMCP(
    name="MLflow Runs",
    instructions="Tools for querying MLflow experiments, runs, metrics, and artifacts. "
    "All tools accept an optional tracking_uri parameter to target a specific MLflow server; "
    "if omitted, the default MLFLOW_TRACKING_URI from the environment is used.",
)


def _client(tracking_uri: Optional[str] = None) -> MlflowClient:
    return MlflowClient(tracking_uri=tracking_uri or DEFAULT_TRACKING_URI)


@mcp.tool
def search_experiments(
    filter_string: Optional[str] = None,
    max_results: int = 100,
    order_by: Optional[list[str]] = None,
    view_type: int = 1,
    tracking_uri: Optional[str] = None,
) -> list[dict]:
    """Search MLflow experiments.

    Args:
        filter_string: Filter expression, e.g. "name = 'my_experiment'" or "tags.team = 'nlp'".
        max_results: Maximum number of experiments to return.
        order_by: List of columns to order by, e.g. ["name ASC", "last_update_time DESC"].
        view_type: 1=ACTIVE_ONLY (default), 2=DELETED_ONLY, 3=ALL.
        tracking_uri: MLflow tracking server URI. Omit to use the default.
    """
    experiments = _client(tracking_uri).search_experiments(
        view_type=view_type,
        max_results=max_results,
        filter_string=filter_string,
        order_by=order_by,
    )
    return [
        {
            "experiment_id": e.experiment_id,
            "name": e.name,
            "artifact_location": e.artifact_location,
            "lifecycle_stage": e.lifecycle_stage,
        }
        for e in experiments
    ]


@mcp.tool
def search_runs(
    experiment_ids: list[str],
    filter_string: str = "",
    max_results: int = 100,
    order_by: Optional[list[str]] = None,
    run_view_type: int = 1,
    page_token: Optional[str] = None,
    tracking_uri: Optional[str] = None,
) -> dict:
    """Search MLflow runs in one or more experiments.

    Args:
        experiment_ids: List of experiment IDs to search within.
        filter_string: Filter expression, e.g. "metrics.rmse < 0.5 AND params.lr = '0.01'".
        max_results: Maximum number of runs to return.
        order_by: List of columns to order by, e.g. ["metrics.rmse DESC", "start_time ASC"].
        run_view_type: 1=ACTIVE_ONLY (default), 2=DELETED_ONLY, 3=ALL.
        page_token: Pagination token from a previous search result.
        tracking_uri: MLflow tracking server URI. Omit to use the default.
    """
    runs = _client(tracking_uri).search_runs(
        experiment_ids=experiment_ids,
        filter_string=filter_string,
        run_view_type=run_view_type,
        max_results=max_results,
        order_by=order_by,
        page_token=page_token,
    )
    results = []
    for r in runs:
        results.append(
            {
                "run_id": r.info.run_id,
                "run_name": r.info.run_name,
                "experiment_id": r.info.experiment_id,
                "status": r.info.status,
                "start_time": r.info.start_time,
                "end_time": r.info.end_time,
                "metrics": r.data.metrics,
                "params": r.data.params,
                "tags": {
                    k: v
                    for k, v in r.data.tags.items()
                    if not k.startswith("mlflow.")
                },
            }
        )
    return {"runs": results, "next_page_token": getattr(runs, "token", None)}


@mcp.tool
def get_run(
    run_id: str,
    tracking_uri: Optional[str] = None,
) -> dict:
    """Get full details of a specific MLflow run.

    Args:
        run_id: The run ID to retrieve.
        tracking_uri: MLflow tracking server URI. Omit to use the default.
    """
    r = _client(tracking_uri).get_run(run_id)
    return {
        "run_id": r.info.run_id,
        "run_name": r.info.run_name,
        "experiment_id": r.info.experiment_id,
        "status": r.info.status,
        "start_time": r.info.start_time,
        "end_time": r.info.end_time,
        "artifact_uri": r.info.artifact_uri,
        "lifecycle_stage": r.info.lifecycle_stage,
        "metrics": r.data.metrics,
        "params": r.data.params,
        "tags": r.data.tags,
    }


@mcp.tool
def get_metric_history(
    run_id: str,
    key: str,
    tracking_uri: Optional[str] = None,
) -> list[dict]:
    """Get the full history of a metric across all steps for a run.

    Args:
        run_id: The run ID.
        key: The metric key name.
        tracking_uri: MLflow tracking server URI. Omit to use the default.
    """
    history = _client(tracking_uri).get_metric_history(run_id, key)
    return [
        {
            "key": m.key,
            "value": m.value,
            "step": m.step,
            "timestamp": m.timestamp,
        }
        for m in history
    ]


@mcp.tool
def list_artifacts(
    run_id: str,
    path: Optional[str] = None,
    tracking_uri: Optional[str] = None,
) -> list[dict]:
    """List artifacts for a run.

    Args:
        run_id: The run ID.
        path: Relative path within the artifact store. Omit for root listing.
        tracking_uri: MLflow tracking server URI. Omit to use the default.
    """
    artifacts = _client(tracking_uri).list_artifacts(run_id, path)
    return [
        {"path": a.path, "is_dir": a.is_dir, "file_size": a.file_size}
        for a in artifacts
    ]


@mcp.tool
def download_artifact(
    run_id: str,
    path: str,
    dst_path: Optional[str] = None,
    tracking_uri: Optional[str] = None,
) -> str:
    """Download an artifact from a run to local disk.

    Args:
        run_id: The run ID.
        path: Relative path to the artifact within the run's artifact store.
        dst_path: Local destination directory. If omitted, uses a temp directory.
        tracking_uri: MLflow tracking server URI. Omit to use the default.

    Returns:
        Local filesystem path to the downloaded artifact.
    """
    return _client(tracking_uri).download_artifacts(run_id, path, dst_path)


def main() -> None:
    """Entry point for the CLI command."""
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
