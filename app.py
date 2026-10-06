import os

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

THINGSPEAK_READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Irrigation Dashboard",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# THINGSPEAK CONFIGURATION
# ============================================================

THINGSPEAK_CHANNEL_ID = 3503497


# Check whether API key is available
if not THINGSPEAK_READ_API_KEY:
    st.error(
        "ThingSpeak Read API Key is missing. "
        "Please add THINGSPEAK_READ_API_KEY to your .env file."
    )
    st.stop()


# ============================================================
# SOIL MOISTURE CALIBRATION
# ============================================================

# Change these after checking your actual ESP8266 readings.
# WET soil gives a lower ADC value and DRY soil gives a higher
# ADC value for the typical setup.

WET_VALUE = 300
DRY_VALUE = 900


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
    }

    h1 {
        color: #ffffff;
    }

    h2 {
        color: #ffffff;
    }

    h3 {
        color: #ffffff;
    }

    .metric-card {
        background-color: #1b1f26;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #30363d;
    }

    .status-on {
        color: #00ff88;
        font-size: 24px;
        font-weight: bold;
    }

    .status-off {
        color: #ff5555;
        font-size: 24px;
        font-weight: bold;
    }

    .info-box {
        background-color: #1b1f26;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.title("🌱 Smart Irrigation Dashboard")

st.write(
    "Real-time monitoring of soil moisture and irrigation status "
    "using ESP8266 + ThingSpeak."
)

st.divider()


# ============================================================
# THINGSPEAK DATA FUNCTION
# ============================================================

@st.cache_data(ttl=10)
def get_thingspeak_data():

    url = (
        f"https://api.thingspeak.com/channels/"
        f"{THINGSPEAK_CHANNEL_ID}/feeds.json"
    )

    params = {
        "api_key": THINGSPEAK_READ_API_KEY,
        "results": 50
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        json_data = response.json()

        feeds = json_data.get("feeds", [])

        if not feeds:
            return pd.DataFrame(), "ThingSpeak returned no data."

        data = []

        for feed in feeds:

            data.append({
                "timestamp": feed.get("created_at"),
                "raw_moisture": feed.get("field1"),
                "pump_status": feed.get("field2"),
                "soil_status": feed.get("field3")
            })

        df = pd.DataFrame(data)

        if df.empty:
            return pd.DataFrame(), "No records found."

        # Convert timestamp
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        # Convert numerical values
        df["raw_moisture"] = pd.to_numeric(
            df["raw_moisture"],
            errors="coerce"
        )

        df["pump_status"] = pd.to_numeric(
            df["pump_status"],
            errors="coerce"
        )

        df["soil_status"] = pd.to_numeric(
            df["soil_status"],
            errors="coerce"
        )

        # Remove invalid rows
        df = df.dropna(
            subset=["timestamp", "raw_moisture"]
        )

        if df.empty:
            return (
                pd.DataFrame(),
                "ThingSpeak data contains no valid readings."
            )

        # Convert raw ADC value to percentage
        df["moisture_percent"] = (
            (DRY_VALUE - df["raw_moisture"])
            / (DRY_VALUE - WET_VALUE)
        ) * 100

        # Keep between 0 and 100
        df["moisture_percent"] = (
            df["moisture_percent"]
            .clip(0, 100)
        )

        return df, None

    except requests.exceptions.Timeout:

        return (
            pd.DataFrame(),
            "ThingSpeak request timed out."
        )

    except requests.exceptions.RequestException as e:

        return (
            pd.DataFrame(),
            f"ThingSpeak connection error: {e}"
        )

    except Exception as e:

        return (
            pd.DataFrame(),
            f"Error: {e}"
        )


# ============================================================
# REFRESH BUTTON
# ============================================================

if st.button("🔄 Refresh Data"):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# GET DATA
# ============================================================

data, error = get_thingspeak_data()


# ============================================================
# ERROR HANDLING
# ============================================================

if error:

    st.error(error)

    st.warning(
        "If your ThingSpeak channel is private, make sure the "
        "READ API KEY in your .env file is correct."
    )

    st.info(
        f"Channel ID: {THINGSPEAK_CHANNEL_ID}"
    )

    st.stop()


# ============================================================
# CURRENT DATA
# ============================================================

latest = data.iloc[-1]

raw_moisture = float(
    latest["raw_moisture"]
)

moisture = float(
    latest["moisture_percent"]
)

pump_value = latest["pump_status"]

soil_value = latest["soil_status"]


# ============================================================
# PUMP STATUS
# ============================================================

if pd.isna(pump_value):

    pump_text = "UNKNOWN"
    pump_on = False

else:

    pump_on = int(float(pump_value)) == 1

    if pump_on:
        pump_text = "ON"
    else:
        pump_text = "OFF"


# ============================================================
# SOIL STATUS
# ============================================================

if not pd.isna(soil_value):

    if int(float(soil_value)) == 1:
        soil_text = "DRY"
    else:
        soil_text = "MOIST"

else:

    # Fallback based on moisture percentage
    if moisture < 35:
        soil_text = "DRY"
    else:
        soil_text = "MOIST"


# ============================================================
# CURRENT STATUS
# ============================================================

st.subheader("📊 Current Status")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🌱 Soil Moisture",
        f"{moisture:.1f}%"
    )


with col2:

    st.metric(
        "📟 Raw Sensor",
        f"{raw_moisture:.0f}"
    )


with col3:

    st.metric(
        "💧 Pump",
        pump_text
    )


with col4:

    st.metric(
        "🌍 Soil",
        soil_text
    )


st.divider()


# ============================================================
# MOISTURE GAUGE
# ============================================================

st.subheader("🌱 Soil Moisture Level")

gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=moisture,
        number={
            "suffix": "%"
        },
        title={
            "text": "Current Soil Moisture"
        },
        gauge={
            "axis": {
                "range": [0, 100]
            },
            "bar": {
                "color": "#00c853"
            },
            "steps": [
                {
                    "range": [0, 35],
                    "color": "#ff5252"
                },
                {
                    "range": [35, 70],
                    "color": "#ffd740"
                },
                {
                    "range": [70, 100],
                    "color": "#69f0ae"
                }
            ],
            "threshold": {
                "line": {
                    "color": "red",
                    "width": 4
                },
                "thickness": 0.75,
                "value": 35
            }
        }
    )
)

gauge.update_layout(
    height=400,
    paper_bgcolor="#0e1117",
    font={
        "color": "white"
    }
)

st.plotly_chart(
    gauge,
    use_container_width=True
)


# ============================================================
# PUMP DISPLAY
# ============================================================

st.subheader("💧 Irrigation Pump")

if pump_on:

    st.markdown(
        '<div class="status-on">🟢 PUMP IS ON</div>',
        unsafe_allow_html=True
    )

    st.write(
        "The irrigation pump is currently running."
    )

else:

    st.markdown(
        '<div class="status-off">🔴 PUMP IS OFF</div>',
        unsafe_allow_html=True
    )

    st.write(
        "The irrigation pump is currently stopped."
    )


# ============================================================
# MOISTURE HISTORY
# ============================================================

st.divider()

st.subheader("📈 Soil Moisture History")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=data["timestamp"],
        y=data["moisture_percent"],
        mode="lines+markers",
        name="Soil Moisture"
    )
)

# Dry threshold
fig.add_hline(
    y=35,
    line_dash="dash",
    annotation_text="Dry Threshold"
)

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Moisture (%)",
    yaxis={
        "range": [0, 100]
    },
    height=450,
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117",
    font={
        "color": "white"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# RAW THINGSPEAK DATA
# ============================================================

with st.expander("📋 View ThingSpeak Data"):

    st.dataframe(
        data,
        use_container_width=True
    )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.divider()

st.subheader("⚙️ System Information")

info_col1, info_col2 = st.columns(2)


with info_col1:

    st.markdown(
        f"""
        <div class="info-box">

        <b>ThingSpeak Channel:</b> {THINGSPEAK_CHANNEL_ID}<br><br>

        <b>Data Source:</b> ESP8266 → ThingSpeak<br><br>

        <b>Records Loaded:</b> {len(data)}

        </div>
        """,
        unsafe_allow_html=True
    )


with info_col2:

    last_update = latest["timestamp"]

    st.markdown(
        f"""
        <div class="info-box">

        <b>Last Update:</b><br>
        {last_update}<br><br>

        <b>Field 1:</b> Soil Moisture<br>
        <b>Field 2:</b> Pump Status<br>
        <b>Field 3:</b> Soil Status

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Smart Irrigation System • ESP8266 • ThingSpeak • Streamlit"
)