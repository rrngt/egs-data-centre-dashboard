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
# BIG, BOLD, CENTERED TITLE (NO ℹ️)
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
# SYSTEM STATUS: ✅ LIVE BLACK & BOLD, PURE HTML (NO ℹ️)
# ----------------------------------------
df = pd.read_csv(DATA_FILE)
if len(df) > 0:
    latest = df.iloc[-1]
    temperature = latest["temperature"]
    humidity = latest["humidity"]
else:
    temperature = "N/A"
    humidity = "N/A"

st.markdown(
    """
    <div style='background: rgba(0, 0, 0, 0.05);
                color: #000000;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;
                font-size: 18px;'>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h2 style='color: #000000; font-weight: bold;'>
        ✅ LIVE
    </h2>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <p style='font-size: 20px; color: #000000;'>
        <span style='font-weight: bold;'>Temperature:</span> {temperature} °C<br>
        <span style='font-weight: bold;'>Humidity:</span> {humidity} %
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# TOTAL RECORDS INSERTED + PASSWORD-PROTECTED DOWNLOAD
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

# Password input
password = st.text_input(
    "Enter password to download CSV:",
    type="password"
)

# Conditional download button
if password == "YourSecretPassword":  # Replace with your actual password
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='data.csv',
        mime='text/csv'
    )
elif password != "":
    st.error("Incorrect password. Please try again.")

# ----------------------------------------
# CLEAN TREND CHARTS — TITLES/TICKS BLACK, PURE HTML TITLES (NO ℹ️)
# ----------------------------------------
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
df = df.dropna(subset=['timestamp', 'temperature', 'humidity'])

# Temperature Trend chart
st.markdown(
    """
    <h3 style='color: #000000; font-size: 24px;'>
        🌡️ Temperature Trend
    </h3>
    """,
    unsafe_allow_html=True
)

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
st.plotly_chart(fig_temp, use_container_width=True)

# Humidity Trend chart
st.markdown(
    """
    <h3 style='color: #000000; font-size: 24px;'>
        💧 Humidity Trend
    </h3>
    """,
    unsafe_allow_html=True
)

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
st.plotly_chart(fig_hum, use_container_width=True)
