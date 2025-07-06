import streamlit as st
import requests
import urllib3
from datetime import datetime
import plotly.graph_objs as go
import pandas as pd
import os

from streamlit_autorefresh import st_autorefresh  # ✅ NEW

# ----------------------------------------
# CONFIG
# ----------------------------------------
st.set_page_config(page_title="EGS DATA CENTER", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------
# AUTO-REFRESH TOGGLE
# ----------------------------------------
st.sidebar.markdown("## Settings")
enable_autorefresh = st.sidebar.checkbox("🔄 Enable Auto-Refresh (Every 1 min)", value=True)

if enable_autorefresh:
    count = st_autorefresh(interval=60 * 1000, limit=None, key="datarefresh")

# ----------------------------------------
# CSV LOGGING SETUP
# ----------------------------------------
DATA_FILE = "data.csv"
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["timestamp", "temperature", "humidity"])
    df_init.to_csv(DATA_FILE, index=False)

# ----------------------------------------
# RESPONSIVE META TAG FOR MOBILE
# ----------------------------------------
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# LIGHT BLUE BACKGROUND
# ----------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #e6f7ff;  /* Light blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# LOGO CENTERED AND BIGGER
# ----------------------------------------
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("logo.png", width=250)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# BIG, BOLD, CENTERED TITLE
# ----------------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #000000; font-size: 64px; font-weight: bold;'>
        EGS DATA CENTER
    </h1>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# FETCH FULL API & OVERWRITE data.csv
# ----------------------------------------
API_URL = "https://iot.egspgroup.in:81/api/dht"

try:
    response = requests.get(API_URL, timeout=10, verify=False)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            rows = []
            for entry in data:
                temperature = entry.get("temperature", "N/A")
                humidity = entry.get("humidity", "N/A")
                timestamp = entry.get("timestamp")

                if not timestamp or pd.isna(timestamp):
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                rows.append([timestamp, temperature, humidity])

            df = pd.DataFrame(rows, columns=["timestamp", "temperature", "humidity"])

            # ✅ Clean, deduplicate, sort
            df.drop_duplicates(subset=["timestamp"], inplace=True)
            df = df.dropna(subset=['timestamp', 'temperature', 'humidity'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors="coerce")
            df = df.dropna(subset=['timestamp'])
            df = df.sort_values(by='timestamp')

            # ✅ Save FULL cleaned data back to CSV
            df.to_csv(DATA_FILE, index=False)

        else:
            st.warning("API returned an empty list.")
    else:
        st.error(f"API error: {response.status_code}")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# ✅ Reload CSV for charts, LIVE, and table
df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'], errors="coerce")
df = df.dropna(subset=['timestamp'])
df = df.sort_values(by='timestamp')

# ----------------------------------------
# SYSTEM STATUS: ✅ LIVE CENTER-ALIGNED + PULSE ANIMATION
# ----------------------------------------
if len(df) > 0:
    latest = df.iloc[-1]
    temperature = latest["temperature"]
    humidity = latest["humidity"]
else:
    temperature = "N/A"
    humidity = "N/A"

# Add the pulse animation style once
st.markdown(
    """
    <style>
      .pulse {
        animation: pulse 2s infinite;
      }
      @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
      }
    </style>
    """,
    unsafe_allow_html=True
)

# Container with center alignment
st.markdown(
    """
    <div style='background: rgba(0, 0, 0, 0.05);
                color: #000000;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;
                font-size: 18px;
                text-align: center;'>
    """,
    unsafe_allow_html=True
)

# LIVE header
st.markdown(
    """
    <h2 style='color: #000000; font-weight: bold; text-align: center;'>
        ✅ LIVE
    </h2>
    """,
    unsafe_allow_html=True
)

# Animated text
st.markdown(
    f"""
    <p class='pulse' style='font-size: 20px; color: #000000; text-align: center;'>
        <span style='font-weight: bold;'>Temperature:</span> {temperature} °C &nbsp;&nbsp;
        <span style='font-weight: bold;'>Humidity:</span> {humidity} %
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# TOTAL RECORDS INSERTED + DOWNLOAD BUTTON
# ----------------------------------------
total_records = len(df)

st.markdown(
    f"""
    <div style='background: rgba(0, 0, 0, 0.05);
                color: #000000;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                font-size: 18px;'>
        <h4>Total Records Inserted: {total_records}</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# CSV bytes
csv = df.to_csv(index=False).encode('utf-8')

# Download button
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name='data.csv',
    mime='text/csv'
)

# ----------------------------------------
# TREND CHARTS — LIVE
# ----------------------------------------
# Temperature Trend chart
fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['temperature'],
    mode='lines+markers',
    line=dict(shape='linear', color='royalblue', width=2),
    marker=dict(size=6),
    name='Temperature'
))
fig_temp.update_layout(
    xaxis_title='Timestamp',
    yaxis_title='Temperature (°C)',
    plot_bgcolor='#e6f7ff',
    paper_bgcolor='#e6f7ff',
    font=dict(color='black', size=14),
    hovermode='x unified',
    xaxis=dict(
        title=dict(font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=True, gridwidth=1, gridcolor='lightgray'
    ),
    yaxis=dict(
        title=dict(font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=True, gridwidth=1, gridcolor='lightgray'
    )
)

# Humidity Trend chart
fig_hum = go.Figure()
fig_hum.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['humidity'],
    mode='lines+markers',
    line=dict(shape='linear', color='dodgerblue', width=2),
    marker=dict(size=6),
    name='Humidity'
))
fig_hum.update_layout(
    xaxis_title='Timestamp',
    yaxis_title='Humidity (%)',
    plot_bgcolor='#e6f7ff',
    paper_bgcolor='#e6f7ff',
    font=dict(color='black', size=14),
    hovermode='x unified',
    xaxis=dict(
        title=dict(font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=True, gridwidth=1, gridcolor='lightgray'
    ),
    yaxis=dict(
        title=dict(font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=True, gridwidth=1, gridcolor='lightgray'
    )
)

# ✅ Display both charts side by side
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <h3 style='color: #000000; font-size: 24px;'>
            🌡️ Temperature Trend
        </h3>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    st.markdown(
        """
        <h3 style='color: #000000; font-size: 24px;'>
            💧 Humidity Trend
        </h3>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(fig_hum, use_container_width=True)

# ----------------------------------------
# ✅ Display All Recorded Data
# ----------------------------------------
st.markdown(
    """
    <h3 style='color: #000000; font-size: 24px;'>
        📋 All Recorded Data
    </h3>
    """,
    unsafe_allow_html=True
)

st.dataframe(
    df.reset_index(drop=True),
    use_container_width=True,
    height=400
)
