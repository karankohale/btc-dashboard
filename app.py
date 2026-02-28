import streamlit as st
import requests

st.title("BTC Open Interest Test")

url = "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"

try:

    r = requests.get(url)

    data = r.json()

    st.write(data)

    st.success("Working ✅")

except Exception as e:

    st.error(e)
