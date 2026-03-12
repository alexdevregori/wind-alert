import os
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone

# Load .env file when running locally
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

# --- Config (set these as GitHub Secrets/Variables) ---
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
LOCATION        = os.environ.get("LOCATION", "San Luis Obispo, CA")
THRESHOLD_MPH   = float(os.environ.get("THRESHOLD_MPH", "20"))
NTFY_TOPIC      = os.environ.get("NTFY_TOPIC", "wind-alert-tunas-house")

ALERT_STATE_FILE = "last_alert_date.txt"

def get_today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def already_alerted_today():
    if not os.path.exists(ALERT_STATE_FILE):
        return False
    with open(ALERT_STATE_FILE) as f:
        return f.read().strip() == get_today()

def save_alert_date():
    with open(ALERT_STATE_FILE, "w") as f:
        f.write(get_today())

def get_wind():
    url = (
        f"https://api.weatherapi.com/v1/current.json"
        f"?key={WEATHER_API_KEY}&q={urllib.parse.quote(LOCATION)}&aqi=no"
    )
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    current  = data["current"]
    location = data["location"]
    return {
        "mph":       current["wind_mph"],
        "direction": current["wind_dir"],
        "gust_mph":  current["gust_mph"],
        "city":      f"{location['name']}, {location['region']}",
    }

def send_notification(wind):
    title = f"Wind alert: {wind['mph']:.0f} mph in {wind['city']}"
    body  = (
        f"{wind['mph']:.0f} mph ({wind['direction']}), "
        f"gusts up to {wind['gust_mph']:.0f} mph. "
        f"Above your {THRESHOLD_MPH:.0f} mph limit — put the umbrella down!"
    )
    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=body.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": "high",
            "Tags": "wind_face",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Notification sent — status {resp.status}")

def main():
    wind = get_wind()
    print(f"Wind in {wind['city']}: {wind['mph']:.1f} mph (threshold: {THRESHOLD_MPH} mph)")

    if wind["mph"] > THRESHOLD_MPH:
        if already_alerted_today():
            print("Wind is high but already sent an alert today — skipping.")
        else:
            print("Threshold exceeded — sending push notification...")
            send_notification(wind)
            save_alert_date()
    else:
        print("Wind is within limit. No alert sent.")

if __name__ == "__main__":
    main()