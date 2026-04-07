import streamlit as st
import requests
import time

# -------------------------------
# CONFIG (3 API KEYS)
# -------------------------------
API_KEYS = [
    "SF26BV822EONZZN7",
    "JATAGYZ0MIGPHLO0",
    "QOUHZ9THRCCQ0DI0"
]

st.set_page_config(page_title="Gold Dashboard", layout="wide")

st.title("🏅 Gold Price Dashboard (ETF vs India Market)")
st.subheader("📅 Live Gold Price (Latest Available Data)")

# -------------------------------
# FUNCTION: FETCH GOLD DATA (SMART RETRY + MULTI-KEY)
# -------------------------------
@st.cache_data(ttl=3600)  # cache for 1 hour
def get_gold_data():
    for key in API_KEYS:
        for attempt in range(2):  # retry each key 2 times
            try:
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={key}"
                response = requests.get(url, timeout=10)
                data = response.json()

                # ✅ Valid response
                if "Time Series (Daily)" in data:
                    return data

                # ❌ Rate limit message → try next key
                if "Information" in data:
                    break

            except:
                time.sleep(1)  # wait before retry

    return None  # all keys failed


# -------------------------------
# FUNCTION: USD DATA
# -------------------------------
@st.cache_data(ttl=3600)
def get_usd_data():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        return requests.get(url, timeout=10).json()
    except:
        return {}


gold_data = get_gold_data()
usd_data = get_usd_data()

# -------------------------------
# PROCESS
# -------------------------------
try:
    if gold_data is None:
        # Clean UI (no red error)
        st.warning("⚠️ Live data temporarily unavailable. Please refresh after some time.")
        st.stop()

    time_series = gold_data["Time Series (Daily)"]

    # ✅ Always get latest available date
    latest_date = list(time_series.keys())[0]

    gold_usd_ounce = float(time_series[latest_date]["4. close"])

    # USD fallback safe
    usd_to_inr = usd_data.get("rates", {}).get("INR", 93.31)

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
    st.write(f"**Last Updated Date:** {latest_date}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌍 ETF / Global Price")
        st.metric("Gold ETF (USD / ounce)", f"${gold_usd_ounce:.2f}")
        st.metric("USD → INR", f"₹{usd_to_inr:.2f}")
        st.metric("Base Gold (INR / gram)", f"₹{gold_inr_gram:.2f}")

    with col2:
        st.markdown("### 🇮🇳 India Market Price")
        st.metric("24K Gold (₹ / gram)", f"₹{gold_24k:,.0f}")
        st.metric("22K Gold (₹ / gram)", f"₹{gold_22k:,.0f}")
        st.metric("18K Gold (₹ / gram)", f"₹{gold_18k:,.0f}")

    # -------------------------------
    # NOTES
    # -------------------------------
    st.info("ETF price is global gold value. India price includes taxes, GST, and market premium.")
    st.caption("Live data reflects latest available trading data (auto-adjusts for weekends/holidays).")

except Exception as e:
    st.warning("⚠️ Temporary issue loading data. Please refresh.")
