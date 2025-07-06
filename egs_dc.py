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
        background: #f5f5f5;  /* light background */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# TITLE + BUTTON STACKED IN FORM
# ----------------------------------------
with st.form(key="get_data_form"):
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1 style='color: #333333; font-size: 60px;'>
                EGS DATA CENTER
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    submitted = st.form_submit_button(
        "🔄 Get Data",
        help="Fetch the latest sensor data"
    )

# ----------------------------------------
# IF BUTTON CLICKED → FETCH DATA & SHOW STATUS + CHARTS
# ----------------------------------------
if submitted:
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
        <div style='background: rgba(0, 0, 0, 0.05);
                    color: #333333;
                    padding: 30px;
                    border-radius: 12px;
                    margin-bottom: 20px;'>
        """,
        unsafe_allow_html=True
    )

    st.subheader("✅Live Data")
    st.write(f"**Temperature Status:** {temperature} °C")
    st.write(f"**Humidity Status:** {humidity} %")
    st.write(f"Last updated: {now}")

    st.markdown("</div>", unsafe_allow_html=True)

    # READ LOGGED DATA
    df = pd.read_csv(DATA_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
    df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
    df = df.dropna(subset=['temperature', 'humidity'])

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
