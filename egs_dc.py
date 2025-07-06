import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import urllib3
from datetime import datetime

# ----------------------------------------
# CONFIG
# ----------------------------------------
st.set_page_config(page_title="EGS DATA CENTER", layout="wide")
REFRESH_INTERVAL = 30  # seconds

# ----------------------------------------
# SET CUSTOM BACKGROUND IMAGE USING CSS
# ----------------------------------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        import base64
    encoded = base64.b64encode(image.read()).decode()
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("data:image/jpg;base64,{encoded}");
             background-size: cover;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Use your image
add_bg_from_local("egs_background.jpg")

# ----------------------------------------
# TITLE
# ----------------------------------------
st.markdown(
    """
    <div style='background: rgba(0, 0, 0, 0.6);
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 20px;'>
        <h1 style='color: white; font-family: Arial, sans-serif; margin: 0;'>
            EGS DATA CENTER
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# BUTTON TO SHOW DATA
# ----------------------------------------
if st.button("📊 Show Data"):
    st.caption(f"Auto-refresh every {REFRESH_INTERVAL} seconds")
    st.write(f"🔄 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ----------------------------------------
    # FETCH DATA
    # ----------------------------------------
    @st.cache_data(ttl=REFRESH_INTERVAL)
    def get_dht_data():
        url = "https://iot.egspgroup.in:81/api/dht"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            return df
        else:
            st.error(f"❌ Failed to fetch data. Status code: {response.status_code}")
            return pd.DataFrame()

    df = get_dht_data()

    if df.empty:
        st.warning("⚠️ No data available.")
        st.stop()

    latest_temp = df['temperature'].iloc[-1]
    latest_humidity = df['humidity'].iloc[-1]
    total_records = len(df)

    def status_color(value, min_val, max_val):
        if value < min_val:
            return "🟦 Low"
        elif value > max_val:
            return "🟥 High"
        else:
            return "🟩 Normal"

    status_temp = status_color(latest_temp, 20, 40)
    status_humidity = status_color(latest_humidity, 30, 60)

    # METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ Latest Temperature (°C)", f"{latest_temp:.1f}°C", status_temp)
    col2.metric("💧 Latest Humidity (%)", f"{latest_humidity:.1f}%", status_humidity)
    col3.metric("📅 Last Data Timestamp", df['timestamp'].max().strftime("%Y-%m-%d %H:%M:%S"))
    col4.metric("📊 Total Records Inserted", f"{total_records}")

    # PLOTLY LINE CHARTS
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("🌡️ Temperature Trend")
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['temperature'],
            mode='lines+markers',
            line=dict(color='royalblue')
        ))
        fig_temp.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Temperature (°C)",
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with chart_col2:
        st.subheader("💧 Humidity Trend")
        fig_humidity = go.Figure()
        fig_humidity.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['humidity'],
            mode='lines+markers',
            line=dict(color='orange')
        ))
        fig_humidity.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Humidity (%)",
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_humidity, use_container_width=True)

    # GAUGES
    st.markdown("---")
    st.subheader("✅ Real-time Gauges")
    gauge_col1, gauge_col2 = st.columns(2)

    with gauge_col1:
        gauge_temp = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=latest_temp,
            title={'text': "Temperature (°C)"},
            delta={'reference': 30},
            gauge={
                'axis': {'range': [0, 50]},
                'bar': {'color': "royalblue"},
                'steps': [
                    {'range': [0, 20], 'color': "lightblue"},
                    {'range': [20, 40], 'color': "lightgreen"},
                    {'range': [40, 50], 'color': "red"}
                ],
            }
        ))
        st.plotly_chart(gauge_temp, use_container_width=True)

    with gauge_col2:
        gauge_humidity = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=latest_humidity,
            title={'text': "Humidity (%)"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "orange"},
                'steps': [
                    {'range': [0, 30], 'color': "lightblue"},
                    {'range': [30, 60], 'color': "lightgreen"},
                    {'range': [60, 100], 'color': "red"}
                ],
            }
        ))
        st.plotly_chart(gauge_humidity, use_container_width=True)

    # RAW DATA
    with st.expander("🔍 View Raw Data"):
        st.dataframe(df, use_container_width=True)

    # STATUS
    st.markdown("---")
    st.subheader("✅ System Status")
    st.write(f"**Temperature Status:** {status_temp}")
    st.write(f"**Humidity Status:** {status_humidity}")
