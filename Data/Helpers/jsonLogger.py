import json
import datetime
import os
log_file = "Data/Helpers/log.json"

def load_logs():
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_logs(logs):
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

def get_next_id(logs):
    return max(log["id"] for log in logs) + 1

def write_log(username, action):
    logs = load_logs()
    log_entry = {
        "id": get_next_id(logs),
        "username": username,
        "action": action,
        "timestamp": datetime.datetime.now().isoformat()
    }
    logs.append(log_entry)
    save_logs(logs)
    return log_entry["id"]

def delete_logs_by_username(username):
    logs = load_logs()
    logs = [log for log in logs if log["username"] != username]
    save_logs(logs)

def delete_log_by_id(log_id):
    logs = load_logs()
    logs = [log for log in logs if log["id"] != log_id]
    save_logs(logs)
