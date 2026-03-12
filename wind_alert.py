import os
import smtplib
import urllib.request
import urllib.parse
import json
from email.mime.text import MIMEText
from datetime import datetime

# --- Config (set these as GitHub Secrets/Variables) ---
WEATHER_API_KEY    = os.environ["WEATHER_API_KEY"]
LOCATION           = os.environ.get("LOCATION", "San Luis Obispo, CA")
THRESHOLD_MPH      = float(os.environ.get("THRESHOLD_MPH", "20"))
GMAIL_ADDRESS      = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

# Your phone number + carrier gateway, e.g. 8055551234@txt.att.net
# See carrier list below in comments
SMS_ADDRESS = os.environ["SMS_ADDRESS"]

# Carrier email-to-SMS gateways:
# AT&T:      number@txt.att.net
# T-Mobile:  number@tmomail.net
# Verizon:   number@vtext.com
# Sprint:    number@messaging.sprintpcs.com
# US Mobile: number@usmobile.com

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
        "time":      datetime.utcnow().strftime("%H:%M UTC"),
    }

def send_sms(wind):
    # Keep under 160 chars so it arrives as a single text
    body = (
        f"Wind alert! {wind['mph']:.0f} mph ({wind['direction']}) "
        f"in {wind['city']} — above your {THRESHOLD_MPH:.0f} mph limit. "
        f"Put the umbrella down!"
    )

    msg = MIMEText(body, "plain")
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = SMS_ADDRESS
    msg["Subject"] = ""  # blank subject — shows as part of SMS body on most carriers

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, SMS_ADDRESS, msg.as_string())

    print(f"SMS sent to {SMS_ADDRESS}")

def main():
    wind = get_wind()
    print(f"Wind in {wind['city']}: {wind['mph']:.1f} mph (threshold: {THRESHOLD_MPH} mph)")

    if wind["mph"] > THRESHOLD_MPH:
        print("Threshold exceeded — sending SMS alert...")
        send_sms(wind)
    else:
        print("Wind is within limit. No alert sent.")

if __name__ == "__main__":
    main()
