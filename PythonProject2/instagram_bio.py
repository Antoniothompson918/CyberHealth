

import os
import time
from instaloader import Instaloader, Profile
from win10toast import ToastNotifier


TARGET_USERNAME = "cyberhealthco"
LAST_BIO_FILE   = "last_bio.txt"
CHECK_INTERVAL  = 10  # seconds between checks (1 hour)


toaster = ToastNotifier()

def get_current_bio(username: str) -> str:

    loader = Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    profile = Profile.from_username(loader.context, username)
    return profile.biography

def read_last_bio() -> str:

    if os.path.isfile(LAST_BIO_FILE):
        with open(LAST_BIO_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return None

def write_last_bio(bio_text: str):

    with open(LAST_BIO_FILE, "w", encoding="utf-8") as f:
        f.write(bio_text)

def notify_change(new_bio: str):

    title = f"@{TARGET_USERNAME} Bio Updated"
    message = f"New bio:\n{new_bio}"
    toaster.show_toast(title, message, duration=10, threaded=True)

    while toaster.notification_active():
        time.sleep(0.1)

def check_and_alert():

    try:
        bio = get_current_bio(TARGET_USERNAME)
    except Exception as e:
        print("Error fetching bio:", e)
        return

    last = read_last_bio()
    if last is None:

        write_last_bio(bio)
        print("Stored initial bio.")
    elif bio != last:
        print("Bio change detected!")
        print("New bio:", bio)
        notify_change(bio)
        write_last_bio(bio)
    else:
        print("No change detected.")

def main():
    print(f"Starting Instagram bio monitor for @{TARGET_USERNAME}")

    check_and_alert()

    while True:
        time.sleep(CHECK_INTERVAL)
        check_and_alert()

if __name__ == "__main__":
    main()


