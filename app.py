import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

st.set_page_config(layout="wide")

st.title("⚡ BTC Dashboard (Cloud Working Version)")


# -----------------
# SAFE GET
# -----------------

def safe_get(url):

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass

    return None


# -----------------
# BTC PRICE
# -----------------

price = safe_get(
"https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
)

btc_price = float(price["price"]) if price else 0

st.metric("BTC Price", btc_price)


# -----------------
# TRADES
# -----------------

trades = safe_get(
"https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=100"
)

if trades:

    df = pd.DataFrame(trades)

    df["price"] = df["price"].astype(float)
    df["qty"] = df["qty"].astype(float)

    whales = df[df.qty > 0.5]

    st.subheader("🐋 Whale Trades")

    st.dataframe(whales)


# -----------------
# DEPTH
# -----------------

depth = safe_get(
"https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=20"
)

if depth:

    bids = pd.DataFrame(depth["bids"], columns=["price","qty"]).astype(float)

    asks = pd.DataFrame(depth["asks"], columns=["price","qty"]).astype(float)

    st.subheader("📚 Liquidity")

    fig = go.Figure()

    fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

    fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

    st.plotly_chart(fig, use_container_width=True)


# -----------------
# REFRESH
# -----------------

if st.button("Refresh"):

    st.rerun()
