import streamlit as st
import requests
import urllib3
from datetime import datetime
import plotly.graph_objs as go

# ----------------------------------------
# CONFIG
# ----------------------------------------
st.set_page_config(page_title="EGS DATA CENTER", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------
# BACKGROUND IMAGE
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

IMAGE_URL = "https://raw.githubusercontent.com/rrngt/egs-data-centre-dashboard/main/egs_background.jpg"
add_bg_from_url(IMAGE_URL)

# ----------------------------------------
# BUTTON: GET DATA
# ----------------------------------------
if st.button("🔄 Get Data"):
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

    # SYSTEM STATUS
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
    st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("</div>", unsafe_allow_html=True)

    # CHART
    st.subheader("📈 Sensor Data Chart")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Temperature", "Humidity"],
        y=[temperature, humidity],
        text=[f"{temperature} °C", f"{humidity} %"],
        textposition='auto'
    ))
    fig.update_layout(
        yaxis=dict(title='Value'),
        xaxis=dict(title='Parameter'),
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Click **Get Data** to fetch and display sensor data.")

