import streamlit as st
import requests

st.title("BTC Test Dashboard")

# Simple CoinGecko API

url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

try:

    r = requests.get(url)

    data = r.json()

    price = data["bitcoin"]["usd"]

    st.success(f"BTC Price: ${price}")

except Exception as e:

    st.error("API failed")
    st.write(e)


if st.button("Refresh"):

    st.rerun()
