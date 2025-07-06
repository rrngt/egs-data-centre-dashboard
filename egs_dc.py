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
# LIGHT BACKGROUND
# ----------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f5f5f5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# LOGO CENTERED AND BIGGER
# ----------------------------------------
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("logo.png", width=250)  # ✅ Adjust size here (200–300 is good)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# BIG, BOLD, CENTERED TITLE
# ----------------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #333333; font-size: 72px; font-weight: bold;'>
        EGS DATA CENTER
    </h1>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# AUTOMATIC FETCH EVERY PAGE LOAD
# ----------------------------------------
API_URL = "https://iot.egspgroup.in:81/api/dht"

try:
    response = requests.get(API_URL, timeout=5, verify=False)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            rows_to_append = []
            for entry in data:
                temperature = entry.get("temperature", "N/A")
                humidity = entry.get("humidity", "N/A")
                timestamp = entry.get("timestamp")

                if not timestamp or pd.isna(timestamp):
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                rows_to_append.append([timestamp, temperature, humidity])

            df_new = pd.DataFrame(rows_to_append, columns=["timestamp", "temperature", "humidity"])
            df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)

            # Remove duplicate timestamps
            df = pd.read_csv(DATA_FILE)
            df.drop_duplicates(subset=["timestamp"], inplace=True)
            df.to_csv(DATA_FILE, index=False)

            st.success(f"✅ Fetched & inserted {len(rows_to_append)} records.")
        else:
            st.warning("API returned an empty list.")
    else:
        st.error(f"API error: {response.status_code}")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# ----------------------------------------
# SYSTEM STATUS: show latest record
# ----------------------------------------
df = pd.read_csv(DATA_FILE)
if len(df) > 0:
    latest = df.iloc[-1]
    temperature = latest["temperature"]
    humidity = latest["humidity"]
    now = latest["timestamp"]
else:
    temperature = "N/A"
    humidity = "N/A"
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

st.markdown(
    """
    <div style='background: rgba(0, 0, 0, 0.05);
                color: #333333;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;'>
    """,
    unsafe_allow_html=True
)

st.subheader("✅ LIVE")
st.write(f"**Temperature Status:** {temperature} °C")
st.write(f"**Humidity Status:** {humidity} %")
st.write(f"Last updated: {now}")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# TOTAL RECORDS INSERTED + DOWNLOAD BUTTON
# ----------------------------------------
total_records = len(df)

st.markdown(
    f"""
    <div style='background: rgba(0, 0, 0, 0.05);
                color: #333333;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;'>
        <h4>Total Records Inserted: {total_records}</h4>
    </div>
    """,
    unsafe_allow_html=True
)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name='data.csv',
    mime='text/csv'
)

# ----------------------------------------
# CHARTS — safe timestamp parsing
# ----------------------------------------
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
df = df.dropna(subset=['timestamp', 'temperature', 'humidity'])

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
        font=dict(color='#333333'),
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
        font=dict(color='#333333'),
        xaxis_tickangle=-45
    )
    fig_hum.update_traces(line=dict(shape='spline'))
    st.plotly_chart(fig_hum, use_container_width=True)
