import logging
import json
import os
from datetime import datetime

# Configure a logger that writes to a file in the workflow directory
LOGGER_NAME = "workflow_tracer"
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(run_id: str = None) -> logging.Logger:
    """Create or retrieve a logger for a specific run.

    Args:
        run_id: Optional identifier for the execution instance. If None, a timestamp is used.
    Returns:
        Configured Logger instance.
    """
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = logging.getLogger(f"{LOGGER_NAME}_{run_id}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    log_path = os.path.join(LOG_DIR, f"trace_{run_id}.log")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # Also output to console for immediate feedback
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug("Tracer initialized for run_id=%s", run_id)
    return logger

def dump_json_log(data: dict, run_id: str) -> str:
    """Write a JSON representation of the pipeline data.

    Returns the path to the JSON file.
    """
    json_path = os.path.join(LOG_DIR, f"trace_{run_id}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_path
