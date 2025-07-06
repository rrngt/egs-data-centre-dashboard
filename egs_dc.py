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
# TITLE WITH OVERLAY
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
st.write(f"**Temperature Status:** placeholder")
st.write(f"**Humidity Status:** placeholder")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# OTHER APP LOGIC GOES HERE
# ----------------------------------------
