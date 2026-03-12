# Wind Alert — GitHub Actions Setup

Checks wind speed every 15 minutes and emails you when it exceeds your limit. No server needed — runs free on GitHub Actions.

---

## Files in this repo

```
wind-alert/
├── wind_alert.py                    # the script
└── .github/
    └── workflows/
        └── wind_alert.yml           # the schedule
```

---

## Step-by-step setup

### 1. Create a free GitHub repo

1. Go to https://github.com/new
2. Name it `wind-alert` (or anything you like)
3. Set it to **Private** (so your secrets stay private)
4. Click **Create repository**

### 2. Upload these files

Upload `wind_alert.py` to the root of the repo, and upload `wind_alert.yml` to `.github/workflows/` (create those folders if needed).

Or clone locally and push:
```bash
git clone https://github.com/YOUR_USERNAME/wind-alert.git
cd wind-alert
# copy the files in, then:
git add .
git commit -m "Add wind alert"
git push
```

### 3. Get a free WeatherAPI key

1. Sign up free at https://www.weatherapi.com/signup.aspx
2. Your API key is on the dashboard — copy it

### 4. Set up Gmail app password

Gmail requires an "App Password" (not your regular password) for SMTP:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Go to https://myaccount.google.com/apppasswords
4. Create a new app password — name it "Wind Alert"
5. Copy the 16-character password shown

### 5. Add GitHub Secrets

In your GitHub repo → **Settings** → **Secrets and variables** → **Actions**:

Add these **Secrets** (sensitive values):

| Secret name        | Value                              |
|--------------------|------------------------------------|
| `WEATHER_API_KEY`  | Your WeatherAPI key                |
| `GMAIL_ADDRESS`    | Your Gmail address                 |
| `GMAIL_APP_PASSWORD` | The 16-char app password         |
| `NOTIFY_EMAIL`     | Email to send alerts to (can be same as Gmail) |

Add these **Variables** (non-sensitive config):

| Variable name   | Value                         |
|-----------------|-------------------------------|
| `LOCATION`      | e.g. `San Luis Obispo, CA`    |
| `THRESHOLD_MPH` | e.g. `20`                     |

### 6. Test it manually

1. In your repo, go to **Actions** tab
2. Click **Wind Speed Alert** in the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Watch the logs — you should see wind data printed, and an email if wind is above your limit

---

## Changing the schedule

Edit `wind_alert.yml` and change the `cron` line:

```yaml
- cron: "*/15 * * * *"   # every 15 minutes (default)
- cron: "*/5 * * * *"    # every 5 minutes
- cron: "0 * * * *"      # every hour
```

Note: GitHub Actions has a minimum of ~1 min between runs, and free accounts get 2,000 minutes/month — every 15 min uses ~2,880 min/month so stay at 15 min or above to stay free.

---

## Troubleshooting

- **No email received?** Check your spam folder. Also verify the app password was copied correctly (no spaces).
- **API error?** Double-check `WEATHER_API_KEY` is set and your WeatherAPI account is active.
- **Location not found?** Try a different format, e.g. `93401` (zip code) or `San Luis Obispo`.
