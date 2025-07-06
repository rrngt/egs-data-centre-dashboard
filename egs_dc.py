import streamlit as st
import requests
import urllib3
from datetime import datetime
import plotly.graph_objs as go
import pandas as pd
import os

# ----------------------------------------
# CONFIG
# ----------------------------------------
st.set_page_config(page_title="EGS DATA CENTER", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------
# CSV LOGGING SETUP
# ----------------------------------------
DATA_FILE = "data.csv"
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["timestamp", "temperature", "humidity"])
    df_init.to_csv(DATA_FILE, index=False)

# ----------------------------------------
# BUTTON
# ----------------------------------------
button_clicked = st.button("🔄 Get Data")

# ----------------------------------------
# CONDITIONAL BACKGROUND OR PLAIN
# ----------------------------------------
if button_clicked:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: #000000;  /* plain black */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(
                rgba(0, 0, 0, 0.6),
                rgba(0, 0, 0, 0.6)
            ),
            url("https://raw.githubusercontent.com/rrngt/egs-data-centre-dashboard/main/egs_background.jpg");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ----------------------------------------
# TITLE ALWAYS CENTERED
# ----------------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: white;'>
        EGS DATA CENTER
    </h1>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# IF BUTTON CLICKED → LOAD DATA & SHOW STATUS + CHARTS
# ----------------------------------------
if button_clicked:
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

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_row = pd.DataFrame([[now, temperature, humidity]], columns=["timestamp", "temperature", "humidity"])
    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)

    # STATUS BOX
    st.markdown(
        """
        <div style='background: rgba(255, 255, 255, 0.15);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    margin-bottom: 20px;'>
        """,
        unsafe_allow_html=True
    )

    st.subheader("✅ System Status")
    st.write(f"**Temperature Status:** {temperature} °C")
    st.write(f"**Humidity Status:** {humidity} %")
    st.write(f"Last updated: {now}")

    st.markdown("</div>", unsafe_allow_html=True)

    # READ LOGGED DATA
    df = pd.read_csv(DATA_FILE)

    # COLUMNS for side-by-side charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌡️ Temperature Trend")
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['temperature'],
            mode='lines+markers',
            name='Temperature (°C)',
            line=dict(color='red', width=3)
        ))
        fig_temp.update_layout(
            yaxis=dict(title='Temperature (°C)'),
            xaxis=dict(title='Timestamp'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_tickangle=-45
        )
        fig_temp.update_traces(line=dict(shape='spline'))
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        st.subheader("💧 Humidity Trend")
        fig_hum = go.Figure()
        fig_hum.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['humidity'],
            mode='lines+markers',
            name='Humidity (%)',
            line=dict(color='blue', width=3)
        ))
        fig_hum.update_layout(
            yaxis=dict(title='Humidity (%)'),
            xaxis=dict(title='Timestamp'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_tickangle=-45
        )
        fig_hum.update_traces(line=dict(shape='spline'))
        st.plotly_chart(fig_hum, use_container_width=True)

else:
    st.info("Click **Get Data** to show sensor data and trends.")
