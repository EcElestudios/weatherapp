import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import pytz

# -------------------------------------------------
# Configuration
# -------------------------------------------------
API_KEY = "50e0ace4ca4444e68c812956251011"
LAT_LON = "25.993217,-97.172555"
UPDATE_INTERVAL = 60          # seconds
COUNTER_KEY = "counter"       # session-state key for the 60-sec counter

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="Starbase Weather", layout="centered")
st.title("Starbase Live Weather")

# -------------------------------------------------
# Initialise counter (replaces the `a` variable)
# -------------------------------------------------
if COUNTER_KEY not in st.session_state:
    st.session_state[COUNTER_KEY] = 0

# -------------------------------------------------
# Auto-refresh logic
# -------------------------------------------------
# Run the API call only once per minute
if st.session_state[COUNTER_KEY] >= 60:
    st.session_state.weather_data = None          # force refresh
    st.session_state[COUNTER_KEY] = 0

# Increment counter on every rerun
st.session_state[COUNTER_KEY] += 1

# -------------------------------------------------
# Cached API call (runs at most once per UPDATE_INTERVAL)
# -------------------------------------------------
@st.cache_data(ttl=UPDATE_INTERVAL, show_spinner=False)
def fetch_weather():
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": API_KEY, "q": LAT_LON, "aqi": "yes"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# -------------------------------------------------
# Get data (fresh every minute)
# -------------------------------------------------
if "weather_data" not in st.session_state or st.session_state.weather_data is None:
    st.session_state.weather_data = fetch_weather()

weather_data = st.session_state.weather_data

# -------------------------------------------------
# ---->  YOUR ORIGINAL CODE (unchanged)  <----
# -------------------------------------------------
a = st.session_state[COUNTER_KEY]               # keep the name you used

# (the `if a == 60` block is now handled by the counter above,
#  so the API call is already done – we just reuse `weather_data`)

mtime = weather_data['location']['localtime']
day_status = weather_data['current']['is_day']
if day_status == 1:
    day_status = 'daytime'
else:
    day_status = 'nighttime'

# Starbase local time (CST/CDT aware)
utc_now = datetime.now(pytz.UTC)
starbase_tz = pytz.timezone("America/Chicago")
starbase_time = utc_now.astimezone(starbase_tz)

atime = starbase_time.timetuple()               # mimics time.gmtime(...)

current_temp_c = weather_data['current']['temp_c']
current_temp_f = weather_data['current']['temp_f']
feelslike_c = weather_data['current']['feelslike_c']
feelslike_f = weather_data['current']['feelslike_f']
precip_mm = weather_data['current']['precip_mm']
precip_in = weather_data['current']['precip_in']
humid = weather_data['current']['humidity']
wind_dir = weather_data['current']['wind_dir']
wind_mph = weather_data['current']['wind_mph']
wind_kph = weather_data['current']['wind_kph']
vis_km = weather_data['current']['vis_km']
vis_miles = weather_data['current']['vis_miles']
epa_index = weather_data['current']['air_quality']['us-epa-index']

if epa_index <= 2:
    aq = 'good'
elif epa_index <= 4:
    aq = 'moderate'
else:
    aq = 'unhealthy'

# <--  EXACTLY YOUR ORIGINAL `all_out` STRING  -->
all_out = f"The time is now {atime[2]}/{atime[1]}/{atime[0]} {atime[3]:02d}:{atime[4]:02d}:{atime[5]:02d} at Starbase. \nThe current data is from {mtime}. \nIt is currently {day_status} at Starbase. \nCurrent temperature: {current_temp_c} C or {current_temp_f} F. \nCurrent temperature feels like: {feelslike_c} C or {feelslike_f} F. \nThe air quality is {aq} with the epa index being {epa_index}. \nPrecipitation: {precip_mm} mm or {precip_in} in. \nThe humidity is {humid}%. \nThe wind direction is {wind_dir}. \nThe current wind speed is {wind_kph} km/h or {wind_mph} mph. \nThe current visibility is {vis_km} km or {vis_miles} miles."

# -------------------------------------------------
# Display
# -------------------------------------------------
st.code(all_out, language="text")   # preserves line-breaks exactly

# Optional: pretty metrics next to the text
col1, col2 = st.columns(2)
with col1:
    st.metric("Temp", f"{current_temp_c}°C", f"{current_temp_f}°F")
    st.metric("Feels", f"{feelslike_c}°C", f"{feelslike_f}°F")
with col2:
    st.metric("Humidity", f"{humid}%")
    st.metric("Wind", f"{wind_kph} kph", f"{wind_mph} mph")

# -------------------------------------------------
# Auto-rerun (every second) so the counter keeps ticking
# -------------------------------------------------
time.sleep(1)
st.rerun()
