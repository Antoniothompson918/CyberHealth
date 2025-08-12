

import os
import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("FEC_API_KEY")
if not API_KEY:
    st.error("FEC_API_KEY not found in .env file.")
    st.stop()

CONTRIBUTOR_NAME = "Jeff Yass"
LAST_ID_FILE = "last_contribution_id.txt"

st.set_page_config(page_title="Jeff Yass FEC Monitor", layout="centered")

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
    if os.path.isfile(LAST_ID_FILE):
        with open(LAST_ID_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_id(contrib_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(contrib_id)

def display_contribution(contribution):
    st.success("Latest Contribution Found:")
    st.markdown(f"""
    - **Name**: {contribution['contributor_name']}
    - **Date**: {contribution['contribution_receipt_date']}
    - **Amount**: ${contribution['contribution_receipt_amount']:,.2f}
    - **Recipient**: {contribution.get('recipient_name', 'N/A')}
    - **State**: {contribution.get('contributor_state', 'N/A')}
    - **City**: {contribution.get('contributor_city', 'N/A')}
    """)

# Title
st.title("🗳️ Jeff Yass FEC Monitor")
st.caption("Live check for new federal contributions reported on fec.gov")

# Manual refresh button
if st.button("🔍 Check for New Contribution"):
    try:
        latest = get_latest_contribution()
        if not latest:
            st.warning("No contributions found.")
        else:
            latest_id = str(latest["transaction_id"])
            last_seen = read_last_id()

            if latest_id != last_seen:
                st.balloons()
                display_contribution(latest)
                write_last_id(latest_id)
            else:
                st.info("No new contributions since last check.")
                display_contribution(latest)
    except Exception as e:
        st.error(f"Error fetching data: {e}")


st.markdown("---")
refresh_rate = st.selectbox("Auto-refresh interval (seconds)", [0, 10, 30, 60], index=0)
if refresh_rate:
    st.experimental_rerun()
