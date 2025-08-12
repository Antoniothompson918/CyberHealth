
import os
import time
import requests
from win10toast import ToastNotifier
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("FEC_API_KEY")
if not API_KEY:
    raise RuntimeError("FEC_API_KEY not found in .env")

CONTRIBUTOR_NAME = "Jeff Yass"
LAST_ID_FILE = "last_contribution_id.txt"
POLL_INTERVAL_SECONDS = 3600   # 1 hour


toaster = ToastNotifier()

def get_latest_contribution():
    url = "https://api.open.fec.gov/v1/schedules/schedule_a/"
    params = {
        "api_key": API_KEY,
        "contributor_name": CONTRIBUTOR_NAME,
        "sort": "-contribution_receipt_date",
        "per_page": 1
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None

def read_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def write_last_id(contrib_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(contrib_id)

def notify_windows(msg):
    try:

        toaster.show_toast("FEC Notification", msg, duration=10, threaded=True)

        while toaster.notification_active():
            time.sleep(0.1)
    except Exception as e:
        print("⚠️ Notification error:", e)

def check_contribution():
    latest = get_latest_contribution()
    if not latest:
        print("No contributions found.")
        return

    tid = str(latest["transaction_id"])
    last_seen = read_last_id()

    if tid != last_seen:
        date   = latest["contribution_receipt_date"]
        amount = latest["contribution_receipt_amount"]
        name   = latest["contributor_name"]
        msg    = f"New contribution by {name}: ${amount} on {date}"
        print(msg)
        notify_windows(msg)
        write_last_id(tid)
    else:
        print("No new contributions.")

def main():
    print("Starting FEC monitor for Jeff Yass...")
    while True:
        check_contribution()
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
