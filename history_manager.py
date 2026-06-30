import json
import os
import uuid

history_file = "history.json"

def load_history():
    if not os.path.exists(history_file):
        return []

    with open(history_file, "r") as f:
        return json.load(f)


def save_msg(role, content):
    history = load_history()
    history.append({
        "id" : str(uuid.uuid4()),
        "role" : role,
        "content": content
    })

    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)


def save_conversation(question, response):
    save_msg("user", question)
    save_msg("assistant", response)


def get_recent_history(limit=20):
    history = load_history()

    return history[-limit:]