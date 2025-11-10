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
COUNTER_KEY = "counter"
SUNRISE_KEY = "sunrise_data"

# -------------------------------------------------
# Page config (theme will be set dynamically)
# -------------------------------------------------
st.set_page_config(page_title="Starbase Weather", layout="centered")

# -------------------------------------------------
# Helper: Get sunrise/sunset (cached for 24h)
# -------------------------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def get_astronomy():
    url = "http://api.weatherapi.com/v1/astronomy.json"
    params = {"key": API_KEY, "q": LAT_LON, "dt": datetime.now(pytz.timezone("America/Chicago")).strftime("%Y-%m-%d")}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        astro = r.json()['astronomy']['astro']
        return astro['sunrise'], astro['sunset']
    except:
        return None, None

# -------------------------------------------------
# Auto Theme Logic
# -------------------------------------------------
def set_theme_based_on_time():
    starbase_tz = pytz.timezone("America/Chicago")
    now_local = datetime.now(starbase_tz)
    current_time = now_local.time()

    # Try to get sunrise/sunset
    sunrise_str, sunset_str = get_astronomy()
    is_day = None

    if sunrise_str and sunset_str:
        try:
            sunrise = datetime.strptime(sunrise_str, "%I:%M %p").time()
            sunset = datetime.strptime(sunset_str, "%I:%M %p").time()
            is_day = sunrise <= current_time <= sunset
        except:
            pass

    # Fallback: use is_day from weather API
    if is_day is None and "weather_data" in st.session_state:
        is_day = st.session_state.weather_data['current']['is_day'] == 1

    # Final fallback: system preference
    if is_day is None:
        return None  # let Streamlit use system preference

    return "light" if is_day else "dark"

# Apply theme
theme = set_theme_based_on_time()
if theme:
    st._config.set_option("theme.base", theme)

st.title("Starbase Live Weather")

# -------------------------------------------------
# Counter for 60-sec API refresh
# -------------------------------------------------
if COUNTER_KEY not in st.session_state:
    st.session_state[COUNTER_KEY] = 0

if st.session_state[COUNTER_KEY] >= 60:
    st.session_state.weather_data = None
    st.session_state[COUNTER_KEY] = 0

st.session_state[COUNTER_KEY] += 1

# -------------------------------------------------
# Fetch weather data (cached)
# -------------------------------------------------
@st.cache_data(ttl=UPDATE_INTERVAL, show_spinner=False)
def fetch_weather():
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": API_KEY, "q": LAT_LON, "aqi": "yes"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

if "weather_data" not in st.session_state or st.session_state.weather_data is None:
    st.session_state.weather_data = fetch_weather()

weather_data = st.session_state.weather_data

# -------------------------------------------------
# YOUR ORIGINAL CODE (all_out) - UNCHANGED
# -------------------------------------------------
a = st.session_state[COUNTER_KEY]

mtime = weather_data['location']['localtime']
day_status = weather_data['current']['is_day']
if day_status == 1:
    day_status = 'daytime'
else:
    day_status = 'nighttime'

utc_now = datetime.now(pytz.UTC)
starbase_tz = pytz.timezone("America/Chicago")
starbase_time = utc_now.astimezone(starbase_tz)
atime = starbase_time.timetuple()

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

all_out = f"The time is now {atime[2]}/{atime[1]}/{atime[0]} {atime[3]:02d}:{atime[4]:02d}:{atime[5]:02d} at Starbase. \nThe current data is from {mtime}. \nIt is currently {day_status} at Starbase. \nCurrent temperature: {current_temp_c} C or {current_temp_f} F. \nCurrent temperature feels like: {feelslike_c} C or {feelslike_f} F. \nThe air quality is {aq} with the epa index being {epa_index}. \nPrecipitation: {precip_mm} mm or {precip_in} in. \nThe humidity is {humid}%. \nThe wind direction is {wind_dir}. \nThe current wind speed is {wind_kph} km/h or {wind_mph} mph. \nThe current visibility is {vis_km} km or {vis_miles} miles."

# -------------------------------------------------
# Display
# -------------------------------------------------
# Show current mode
current_mode = "Light" if (theme == "light" or (theme is None and "light" in st.get_option("theme.base"))) else "Dark"

st.code(all_out, language="text")

# -------------------------------------------------
# Auto-rerun every second
# -------------------------------------------------
time.sleep(1)
st.rerun()
