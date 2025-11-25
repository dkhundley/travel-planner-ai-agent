# Travel Planner AI Agent

This repo contains a Strands agent that emits OpenTelemetry spans via the built-in `StrandsTelemetry` helper and captures every span (agent, cycles, model calls, tools) in a local JSONL file for offline analysis.

## 1. Install dependencies

```bash
cd /Users/dkhundley/Documents/Repositories/travel-planner-ai-agent
python -m venv .venv
source .venv/bin/activate
pip install -r dependencies/requirements.txt
```

## 2. Configure environment

Set the keys required by OpenAI, plus any OTLP exporter settings you want to use. Example `.env` snippet:

```bash
export OPENAI_API_KEY="sk-..."
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318/v1/traces"   # optional
export OTEL_EXPORTER_OTLP_HEADERS="api-key=local"                       # optional
```

If you set the OTLP endpoint, make sure an OpenTelemetry collector (or compatible APM) is listening on that address.

## 3. Run the agent with telemetry

```bash
source .venv/bin/activate
python src/strands_agent.py
```

What happens on each run:

- `StrandsTelemetry` writes every generated span (agent, event loop cycles, model calls, tool executions) into `src/agent_traces.jsonl` using the console exporter.
- If an OTLP endpoint is configured and not disabled, the same spans are shipped to your collector/observability UI.
- The raw agent responses are still printed to the console for quick verification.

### JSONL only (skip OTLP)

If you just want the local `agent_traces.jsonl` output without connecting to an OTLP collector, disable the exporter at runtime:

```bash
DISABLE_OTEL_EXPORT=1 python src/strands_agent.py
```

With the flag set, the script skips OTLP setup but still executes the agent flow and writes the JSONL log.

## 4. Troubleshooting

- Ensure your OTLP collector is running locally (for example, the OpenTelemetry Collector container exposing port `4318`) before executing the agent with exporting enabled.
- Missing packages? Re-run `pip install -r dependencies/requirements.txt` inside the `.venv`.
- Still seeing connection errors? Either start the collector, update `OTEL_EXPORTER_OTLP_ENDPOINT`, or set `DISABLE_OTEL_EXPORT=1` to run in JSONL-only mode.

