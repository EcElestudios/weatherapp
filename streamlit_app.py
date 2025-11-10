import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import pytz

# --- Configuration ---
API_KEY = "50e0ace4ca4444e68c812956251011"  # Consider using st.secrets for production
LAT_LON = "25.993217,-97.172555"
UPDATE_INTERVAL = 60  # seconds

# --- Page Config ---
st.set_page_config(page_title="Starbase Weather Monitor", layout="centered")
st.title("🌤️ Starbase Live Weather")
st.markdown("**Location:** Starbase, TX (25.993217, -97.172555)")

# --- Cache the API call ---
@st.cache_data(ttl=UPDATE_INTERVAL, show_spinner="Fetching latest weather...")
def get_weather_data():
    url = f"http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": LAT_LON,
        "aqi": "yes"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch weather data: {e}")
        return None

# --- Main App ---
placeholder = st.empty()

# Auto-refresh every UPDATE_INTERVAL seconds
if 'last_update' not in st.session_state:
    st.session_state.last_update = 0

current_time = time.time()
if current_time - st.session_state.last_update >= UPDATE_INTERVAL:
    st.session_state.last_update = current_time
    st.rerun()

# Fetch data
weather_data = get_weather_data()

if weather_data:
    current = weather_data['current']
    location = weather_data['location']

    # Local time at Starbase (assumed US Central Time: UTC-6 or UTC-5 during DST)
    localtime_str = location['localtime']
    local_dt = datetime.strptime(localtime_str, "%Y-%m-%d %H:%M")
    tz = pytz.timezone("America/Chicago")
    local_dt = tz.localize(local_dt)

    # UTC time adjusted to Starbase local
    utc_now = datetime.utcnow()
    starbase_time = utc_now - timedelta(hours=6)  # Approximate CST

    # Day/Night
    day_status = "daytime" if current['is_day'] == 1 else "nighttime"

    # Air Quality
    epa_index = current['air_quality']['us-epa-index']
    if epa_index <= 2:
        aq = 'Good'
        color = "🟢"
    elif epa_index <= 4:
        aq = 'Moderate'
        color = "🟡"
    else:
        aq = 'Unhealthy'
        color = "🔴"

    # Display
    with placeholder.container():
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{current['temp_c']}°C", f"{current['temp_f']}°F")
            st.metric("Feels Like", f"{current['feelslike_c']}°C", f"{current['feelslike_f']}°F")
        with col2:
            st.metric("Humidity", f"{current['humidity']}%")
            st.metric("Wind Speed", f"{current['wind_kph']} kph", f"{current['wind_mph']} mph")

        st.markdown(f"### {color} Air Quality: **{aq}** (EPA Index: {epa_index})")
        st.markdown(f"**Wind Direction:** {current['wind_dir']}")
        st.markdown(f"**Precipitation:** {current['precip_mm']} mm ({current['precip_in']} in)")
        st.markdown(f"**Visibility:** {current['vis_km']} km ({current['vis_miles']} mi)")

        st.info(f"""
        **Starbase Local Time:** {local_dt.strftime('%Y-%m-%d %H:%M')}  
        **It is currently:** {day_status}  
        **Data updated:** {datetime.now().strftime('%H:%M:%S')}
        """)

        # Auto-refresh countdown
        next_update = int(UPDATE_INTERVAL - (current_time - st.session_state.last_update))
        st.caption(f"Next update in {max(next_update, 0)} seconds...")

else:
    st.warning("Waiting for weather data...")
