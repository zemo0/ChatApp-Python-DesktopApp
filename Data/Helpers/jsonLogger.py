import json
import datetime
import os
log_file = "Data/Helpers/log.json"

def loadLogs():
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Greška kod čitanja jsona, preskoči")
            return []
    return []

def saveLogs(logs):
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

def getNextID(logs):
    return max(log["id"] for log in logs) + 1

def writeLog(username, action):
    logs = loadLogs()
    log_entry = {
        "id": getNextID(logs),
        "username": username,
        "action": action,
        "timestamp": datetime.datetime.now().isoformat()
    }
    logs.append(log_entry)
    saveLogs(logs)
    return log_entry["id"]

def deleteLogByUsername(username):
    logs = loadLogs()
    logs = [log for log in logs if log["username"] != username]
    saveLogs(logs)

def deleteLogByID(log_id):
    logs = loadLogs()
    logs = [log for log in logs if log["id"] != log_id]
    saveLogs(logs)
