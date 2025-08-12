

import os
import time
import imaplib
import email
from email.header import decode_header
from win10toast import ToastNotifier
from dotenv import load_dotenv


IMAP_SERVER     = "imap.gmail.com"
MAILBOX         = "INBOX"
ALERT_FROM      = "googlealerts-noreply@google.com"
CHECK_INTERVAL  = 10      # seconds
LAST_UID_FILE   = "last_alert_uid.txt"


load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
if not EMAIL_USER or not EMAIL_PASS:
    raise RuntimeError("EMAIL_USER and EMAIL_PASS must be set in .env")


toaster = ToastNotifier()

def read_last_uid():

    if os.path.isfile(LAST_UID_FILE):
        with open(LAST_UID_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_uid(uid):

    with open(LAST_UID_FILE, "w") as f:
        f.write(str(uid))

def notify(title, message):

    toaster.show_toast(title, message, duration=10, threaded=True)
    # wait for it to finish showing
    while toaster.notification_active():
        time.sleep(0.1)

def check_for_alerts():

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select(MAILBOX)


    status, data = mail.uid('search', None, f'(FROM "{ALERT_FROM}")')
    if status != 'OK':
        print("IMAP UID search failed:", status)
        mail.logout()
        return

    all_uids = [int(u) for u in data[0].split()]
    if not all_uids:
        print("— no Google Alerts ever found.")
        mail.logout()
        return

    last_uid = read_last_uid()
    new_uids = sorted(u for u in all_uids if last_uid is None or u > int(last_uid))

    if not new_uids:
        print(f"— no new Google Alerts since UID {last_uid}")
    else:
        for uid in new_uids:
            status, msg_data = mail.uid('fetch', str(uid), '(RFC822)')
            if status != 'OK':
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subj, enc = decode_header(msg['Subject'])[0]
            if isinstance(subj, bytes):
                subj = subj.decode(enc or 'utf-8', errors='ignore')

            print(f"🔔 New Alert (UID {uid}): {subj}")
            notify("New Google Alert", subj)
            # Mark as read
            mail.uid('store', str(uid), '+FLAGS', '(\\Seen)')


        write_last_uid(max(new_uids))

    mail.logout()

def main():
    print("Starting Google Alert monitor…")

    check_for_alerts()

    while True:
        time.sleep(CHECK_INTERVAL)
        check_for_alerts()

if __name__ == "__main__":
    main()
