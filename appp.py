import streamlit as st
import requests

# -------------------------------
# CONFIG
# -------------------------------
API_KEY = "SF26BV822EONZZN7"

st.set_page_config(page_title="Gold Dashboard", layout="wide")

st.title("🏅 Gold Price Dashboard (ETF vs India Market)")

# -------------------------------
# DATE INPUT
# -------------------------------
selected_date = st.date_input("Select Date")
selected_date_str = selected_date.strftime("%Y-%m-%d")

# -------------------------------
# FETCH GOLD ETF DATA
# -------------------------------
gold_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={API_KEY}"
gold_data = requests.get(gold_url).json()

# -------------------------------
# FETCH USD → INR
# -------------------------------
usd_url = "https://api.exchangerate-api.com/v4/latest/USD"
usd_data = requests.get(usd_url).json()
usd_to_inr = usd_data["rates"]["INR"]

# -------------------------------
# PROCESS
# -------------------------------
try:
    time_series = gold_data["Time Series (Daily)"]

    if selected_date_str in time_series:

        # ETF price (USD/ounce)
        gold_usd_ounce = float(time_series[selected_date_str]["4. close"])

        # Convert to INR per gram (base price)
        gold_inr_gram = (gold_usd_ounce * usd_to_inr) / 31.1035

        # -------------------------------
        # INDIA MARKET ADJUSTMENT
        # -------------------------------
        # Multiplier to match real Indian price
        multiplier = 11.5

        gold_24k = gold_inr_gram * multiplier
        gold_22k = gold_24k * 0.916
        gold_18k = gold_24k * 0.75

        # -------------------------------
        # DISPLAY
        # -------------------------------
        st.subheader(f"📅 {selected_date_str}")

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

        # INFO NOTE
        st.info("ETF price is global gold value. India price includes taxes, GST, and market premium.")

    else:
        st.warning("No data available for selected date")

except:
    st.error("Error fetching data. Try again later.")