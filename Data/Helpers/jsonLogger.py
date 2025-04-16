import json
import datetime
import os


def write_log(message, level="INFO", log_file="log.json"):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "level": level,
        "message": message
    }

    # Append to existing log file or create a new list
    logs = []

    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)
