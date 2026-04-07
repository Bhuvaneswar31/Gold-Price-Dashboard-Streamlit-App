import streamlit as st
import requests
import pandas as pd
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

# -------------------------------
# MODE SELECTION
# -------------------------------
mode = st.radio("Select Mode", ["Live Data", "Select Date"])

if mode == "Select Date":
    selected_date = st.date_input("Select Date")
    selected_date_str = selected_date.strftime("%Y-%m-%d")
else:
    selected_date_str = None

# -------------------------------
# FETCH GOLD DATA (MULTI-KEY)
# -------------------------------
@st.cache_data(ttl=3600)
def get_gold_data():
    for key in API_KEYS:
        for _ in range(2):
            try:
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={key}"
                data = requests.get(url, timeout=10).json()

                if "Time Series (Daily)" in data:
                    return data

                if "Information" in data:
                    break
            except:
                time.sleep(1)
    return None


@st.cache_data(ttl=3600)
def get_usd_data():
    try:
        return requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
    except:
        return {}

gold_data = get_gold_data()
usd_data = get_usd_data()

# -------------------------------
# PROCESS
# -------------------------------
try:
    if gold_data is None:
        st.warning("⚠️ Live data temporarily unavailable. Please refresh.")
        st.stop()

    time_series = gold_data["Time Series (Daily)"]

    # Convert to DataFrame for trend chart
    df = pd.DataFrame(time_series).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df["price"] = df["4. close"].astype(float)

    latest_date = df.index[-1]
    latest_price = df.loc[latest_date]["price"]

    # -------------------------------
    # SELECTED DATE LOGIC
    # -------------------------------
    if selected_date_str:
        selected_dt = pd.to_datetime(selected_date_str)

        if selected_dt in df.index:
            selected_price = df.loc[selected_dt]["price"]
            final_date = selected_dt
        else:
            st.warning("Selected date not available. Showing latest data.")
            selected_price = latest_price
            final_date = latest_date
    else:
        selected_price = latest_price
        final_date = latest_date

    # USD conversion
    usd_to_inr = usd_data.get("rates", {}).get("INR", 93.31)

    gold_inr_gram = (selected_price * usd_to_inr) / 31.1035

    multiplier = 11.5
    gold_24k = gold_inr_gram * multiplier
    gold_22k = gold_24k * 0.916
    gold_18k = gold_24k * 0.75

    # -------------------------------
    # DISPLAY
    # -------------------------------
    st.write(f"**Data Date:** {final_date.date()}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌍 ETF / Global Price")
        st.metric("Selected Price (USD)", f"${selected_price:.2f}")

        # ✅ Comparison with latest
        delta = selected_price - latest_price
        st.metric("Latest Price (USD)", f"${latest_price:.2f}", f"{delta:.2f}")

    with col2:
        st.markdown("### 🇮🇳 India Market Price")
        st.metric("24K Gold", f"₹{gold_24k:,.0f}")
        st.metric("22K Gold", f"₹{gold_22k:,.0f}")
        st.metric("18K Gold", f"₹{gold_18k:,.0f}")

    # -------------------------------
    # TREND CHART
    # -------------------------------
    st.markdown("### 📈 Gold Price Trend (Last 30 Days)")
    st.line_chart(df["price"].tail(30))

    # -------------------------------
    # NOTES
    # -------------------------------
    st.info("ETF price is global gold value. India price includes taxes and market premium.")
    st.caption("Live data reflects latest available trading data.")

except Exception as e:
    st.warning("⚠️ Temporary issue loading data. Please refresh.")
