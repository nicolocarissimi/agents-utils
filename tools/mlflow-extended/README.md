# mlflow-extended-mcp-server

An MCP server that exposes MLflow experiments, runs, metrics, and artifacts as tools for LLM agents.

## Features

- **search_experiments** — Find experiments by name, tags, or lifecycle stage
- **search_runs** — Query runs with filters on metrics, params, and tags
- **get_run** — Get full details of a specific run
- **get_metric_history** — Retrieve the full step-by-step history of a metric
- **list_artifacts** — Browse a run's artifact store
- **download_artifact** — Download artifacts to local disk

All tools accept an optional `tracking_uri` parameter. If omitted, the server
uses the `MLFLOW_TRACKING_URI` environment variable (default: `http://localhost:5000`).

## Installation

### pipx (recommended — isolated from your project)

```bash
pipx install mlflow-extended-mcp-server
```

or from git

```bash
pipx install "mlflow-extended-mcp-server @ git+https://github.com/nicolocarissimi/agents-utils.git#subdirectory=tools/mlflow-extended"
```

### uv

```bash
uv tool install mlflow-extended-mcp-server
```

### pip

```bash
pip install mlflow-extended-mcp-server
```


## Usage

### As a CLI tool

```bash
# Uses MLFLOW_TRACKING_URI from environment, or defaults to http://localhost:5000
mlflow-extended-mcp-server

# Point to a specific MLflow instance
MLFLOW_TRACKING_URI=http://mlflow.internal:5000 mlflow-extended-mcp-server
```

### With Claude Code

Add to your `.claude/settings.json` (or `.claude/settings.local.json`):

```json
{
  "mcpServers": {
    "mlflow-extended": {
      "command": "mlflow-extended-mcp-server",
      "env": {
        "MLFLOW_TRACKING_URI": "http://localhost:5000"
      }
    }
  }
}
```

If you installed with pipx or uv tool, the `mlflow-extended-mcp-server` command is
already on your PATH. No need to specify a Python interpreter.

### Direct Python invocation (without installing)

```bash
MLFLOW_TRACKING_URI=http://localhost:5000 python -m mlflow_extended_mcp_server.server
```
