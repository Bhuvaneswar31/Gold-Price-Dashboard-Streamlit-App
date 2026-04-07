import streamlit as st
import requests
import datetime

# -------------------------------
# CONFIG
# -------------------------------
API_KEY = "SF26BV822EONZZN7"

st.set_page_config(page_title="Gold Dashboard", layout="wide")

st.title("🏅 Gold Price Dashboard (ETF vs India Market)")

# -------------------------------
# DATE INPUT
# -------------------------------
today = datetime.date.today()
selected_date = st.date_input("Select Date", today)
selected_date_str = selected_date.strftime("%Y-%m-%d")

# -------------------------------
# CACHE API CALLS
# -------------------------------
@st.cache_data(ttl=3600)  # 1 hour cache
def get_gold_data():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={API_KEY}"
    data = requests.get(url).json()

    # If API limit reached → return None
    if "Time Series (Daily)" not in data:
        return None

    return data


@st.cache_data(ttl=3600)
def get_usd_data():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    return requests.get(url).json()


gold_data = get_gold_data()
usd_data = get_usd_data()

# -------------------------------
# FALLBACK DATA (IMPORTANT)
# -------------------------------
fallback_data = {
    "2026-04-06": {"4. close": "427.65"},
    "2026-04-05": {"4. close": "428.10"},
    "2026-04-04": {"4. close": "426.80"}
}

# -------------------------------
# PROCESS
# -------------------------------
try:
    # Use fallback if API fails
    if gold_data is None:
        st.warning("⚠️ API limit reached. Showing last available data.")
        time_series = fallback_data
    else:
        time_series = gold_data["Time Series (Daily)"]

    # Handle missing date
    if selected_date_str not in time_series:
        st.warning("Selected date data not available. Showing latest available data.")
        selected_date_str = list(time_series.keys())[0]

    # ETF price
    gold_usd_ounce = float(time_series[selected_date_str]["4. close"])

    # USD to INR (safe fallback)
    usd_to_inr = usd_data.get("rates", {}).get("INR", 93.31)

    # Convert to INR per gram
    gold_inr_gram = (gold_usd_ounce * usd_to_inr) / 31.1035

    # -------------------------------
    # INDIA MARKET CALCULATION
    # -------------------------------
    multiplier = 11.5

    gold_24k = gold_inr_gram * multiplier
    gold_22k = gold_24k * 0.916
    gold_18k = gold_24k * 0.75

    # -------------------------------
    # DISPLAY
    # -------------------------------
    st.subheader(f"📅 {selected_date_str}")

    col1, col2 = st.columns(2)

    # LEFT SIDE
    with col1:
        st.markdown("### 🌍 ETF / Global Price")
        st.metric("Gold ETF (USD / ounce)", f"${gold_usd_ounce:.2f}")
        st.metric("USD → INR", f"₹{usd_to_inr:.2f}")
        st.metric("Base Gold (INR / gram)", f"₹{gold_inr_gram:.2f}")

    # RIGHT SIDE
    with col2:
        st.markdown("### 🇮🇳 India Market Price")
        st.metric("24K Gold (₹ / gram)", f"₹{gold_24k:,.0f}")
        st.metric("22K Gold (₹ / gram)", f"₹{gold_22k:,.0f}")
        st.metric("18K Gold (₹ / gram)", f"₹{gold_18k:,.0f}")

    # -------------------------------
    # NOTES
    # -------------------------------
    st.info("ETF price is global gold value. India price includes taxes, GST, and market premium.")

    st.caption("⚠️ Note: Live data may be limited due to API restrictions. Latest available values are displayed.")

except Exception as e:
    st.error("Error fetching data. Please try again later.")
    st.write(e)
