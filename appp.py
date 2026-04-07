import streamlit as st
import requests

# -------------------------------
# CONFIG
# -------------------------------
API_KEY = "SF26BV822EONZZN7"

st.set_page_config(page_title="Gold Dashboard", layout="wide")

st.title("🏅 Gold Price Dashboard (ETF vs India Market)")

st.subheader("📅 Live Gold Price (Latest Available Data)")

# -------------------------------
# CACHE API CALLS (reduce limit usage)
# -------------------------------
@st.cache_data(ttl=3600)  # 1 hour cache
def get_gold_data():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={API_KEY}"
    return requests.get(url).json()


@st.cache_data(ttl=3600)
def get_usd_data():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    return requests.get(url).json()


gold_data = get_gold_data()
usd_data = get_usd_data()

# -------------------------------
# PROCESS LIVE DATA
# -------------------------------
try:
    # ✅ Validate API response
    if "Time Series (Daily)" not in gold_data:
        st.error("API limit reached or unable to fetch live data.")
        st.write(gold_data)  # Debug info
        st.stop()

    time_series = gold_data["Time Series (Daily)"]

    # ✅ Always take latest available date
    latest_date = list(time_series.keys())[0]

    # ETF price (USD/ounce)
    gold_usd_ounce = float(time_series[latest_date]["4. close"])

    # USD to INR
    usd_to_inr = usd_data.get("rates", {}).get("INR", None)

    if usd_to_inr is None:
        st.error("Error fetching USD to INR rate.")
        st.stop()

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
    st.write(f"**Last Updated Date:** {latest_date}")

    col1, col2 = st.columns(2)

    # LEFT SIDE (ETF DATA)
    with col1:
        st.markdown("### 🌍 ETF / Global Price")
        st.metric("Gold ETF (USD / ounce)", f"${gold_usd_ounce:.2f}")
        st.metric("USD → INR", f"₹{usd_to_inr:.2f}")
        st.metric("Base Gold (INR / gram)", f"₹{gold_inr_gram:.2f}")

    # RIGHT SIDE (INDIA MARKET)
    with col2:
        st.markdown("### 🇮🇳 India Market Price")
        st.metric("24K Gold (₹ / gram)", f"₹{gold_24k:,.0f}")
        st.metric("22K Gold (₹ / gram)", f"₹{gold_22k:,.0f}")
        st.metric("18K Gold (₹ / gram)", f"₹{gold_18k:,.0f}")

    # -------------------------------
    # NOTES
    # -------------------------------
    st.info("ETF price is global gold value. India price includes taxes, GST, and market premium.")

    st.caption("Live data reflects the latest available trading data from global markets (may not update on weekends/holidays).")

except Exception as e:
    st.error("Error fetching live data. Please try again later.")
    st.write(e)
