import streamlit as st
import requests
import urllib3
from datetime import datetime

# ----------------------------------------
# CONFIG
# ----------------------------------------
st.set_page_config(page_title="EGS DATA CENTER", layout="wide")
REFRESH_INTERVAL = 30  # seconds

# ----------------------------------------
# SET CUSTOM BACKGROUND IMAGE USING RAW URL
# ----------------------------------------
def add_bg_from_url(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Use the hosted raw image
IMAGE_URL = "https://raw.githubusercontent.com/rrngt/egs-data-centre-dashboard/main/egs_background.jpg"
add_bg_from_url(IMAGE_URL)

# ----------------------------------------
# DISABLE SSL WARNINGS FOR SELF-SIGNED CERT
# ----------------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------
# FETCH SENSOR DATA FROM YOUR API (LIST FORMAT)
# ----------------------------------------

API_URL = "https://iot.egspgroup.in:81/api/dht"

try:
    response = requests.get(API_URL, timeout=5, verify=False)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            temperature = data[0].get("temperature", "N/A")
            humidity = data[0].get("humidity", "N/A")
        else:
            temperature = "N/A"
            humidity = "N/A"
            st.warning("API returned an empty list.")
    else:
        temperature = "N/A"
        humidity = "N/A"
        st.error(f"API error: {response.status_code}")
except Exception as e:
    temperature = "N/A"
    humidity = "N/A"
    st.error(f"Error fetching data: {e}")

# ----------------------------------------
# SYSTEM STATUS WRAPPED IN DARK BOX
# ----------------------------------------
st.markdown(
    """
    <div style='background: rgba(0, 0, 0, 0.5);
                padding: 20px;
                border-radius: 8px;
                display: inline-block;'>
    """,
    unsafe_allow_html=True
)

st.subheader("✅ System Status")
st.write(f"**Temperature Status:** {temperature} °C")
st.write(f"**Humidity Status:** {humidity} %")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# LAST UPDATED TIME
# ----------------------------------------
st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
