import connexion
import json
import os
from datetime import datetime

from connexion import NoContent

# Constants
EVENT_FILE = "events.json"
MAX_EVENTS = 5

# این همون فانکشن هندلر برای یک endpoint هست
def post_event(body):
    # اینجا منطق اصلی endpoint رو پیاده کن

    return {"message": "Hello, OpenAPI!", "body": body}


def post_login_event(body):
    # body شامل داده‌ی POST هست (json ورودی)


    msg_data = (
        f"User {body['userId']} with client id '{body['clientId']}' logged in. "
    )
    log_event("login", msg_data)

    return {"message": "Login event received", "data": body}

def post_score_event(body):
    # body شامل داده‌ی POST هست (json ورودی)
    msg_data = (
        f"User {body['userId']} with client id '{body['clientId']}' scored {body['score']} in level {body['levelId']}. "
    )
    log_event("score", msg_data)

    return {"message": "Source event received", "data": body}

def get_health(body):
    # body شامل داده‌ی POST هست (json ورودی)
    return {"message": "Health event received", "data": body}



def load_event_data():
    """Load existing event data or initialize if file doesn't exist."""
    if os.path.exists(EVENT_FILE):
        with open(EVENT_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "num_logins": 0,
            "recent_logins": [],
            "num_scores": 0,
            "recent_scores": []
        }



def save_event_data(data):
    """Save event data to file."""
    with open(EVENT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def log_event(event_type, event_message):
    """Logs an event to the JSON file."""
    data = load_event_data()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    event = {
        "msg_data": event_message,
        "received_timestamp": timestamp
    }

    if event_type == "login":
        data["num_logins"] += 1
        data["recent_logins"].insert(0, event)
        if len(data["recent_logins"]) > MAX_EVENTS:
            data["recent_logins"].pop()
    elif event_type == "score":
        data["num_scores"] += 1
        data["recent_scores"].insert(0, event)
        if len(data["recent_scores"]) > MAX_EVENTS:
            data["recent_scores"].pop()

    save_event_data(data)
    print("Logged:", json.dumps(event, indent=4))




# ساختن app در سطح ماژول
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(
    "openapi.yml",
    strict_validation=True,
    validate_responses=True
)

if __name__ == "__main__":
    app.run(port=8080)
