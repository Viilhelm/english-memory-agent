import os
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from english_memory_agent.app_utils.telemetry import setup_telemetry
from english_memory_agent.app_utils.typing import Feedback

setup_telemetry()

from english_memory_agent.tools.memory_tools import init_db
init_db()

# Handle optional google cloud logger
try:
    import google.auth
    from google.cloud import logging as google_cloud_logging
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
except Exception:
    import logging
    logger = logging.getLogger(__name__)
    # Fallback to standard logging
    logger.log_struct = lambda d, severity: logging.info(f"{severity}: {d}")

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=False,
)
app.title = "english-memory-agent"
app.description = "API for interacting with the English Memory Agent"

@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
