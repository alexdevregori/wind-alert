import os
import smtplib
import urllib.request
import urllib.parse
import json
from email.mime.text import MIMEText
from datetime import datetime, timezone

# --- Config (set these as GitHub Secrets/Variables) ---
WEATHER_API_KEY    = os.environ["WEATHER_API_KEY"]
LOCATION           = os.environ.get("LOCATION", "San Luis Obispo, CA")
THRESHOLD_MPH      = float(os.environ.get("THRESHOLD_MPH", "20"))
GMAIL_ADDRESS      = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
SMS_ADDRESS        = os.environ["SMS_ADDRESS"]

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

def send_sms(wind):
    body = (
        f"Wind alert! {wind['mph']:.0f} mph ({wind['direction']}) "
        f"in {wind['city']} — above your {THRESHOLD_MPH:.0f} mph limit. "
        f"Put the umbrella down!"
    )
    msg = MIMEText(body, "plain")
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = SMS_ADDRESS
    msg["Subject"] = ""

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, SMS_ADDRESS, msg.as_string())

    print(f"SMS sent to {SMS_ADDRESS}")

def main():
    wind = get_wind()
    print(f"Wind in {wind['city']}: {wind['mph']:.1f} mph (threshold: {THRESHOLD_MPH} mph)")

    if wind["mph"] > THRESHOLD_MPH:
        if already_alerted_today():
            print("Wind is high but already sent an alert today — skipping.")
        else:
            print("Threshold exceeded — sending SMS alert...")
            send_sms(wind)
            save_alert_date()
    else:
        print("Wind is within limit. No alert sent.")

if __name__ == "__main__":
    main()