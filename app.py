import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import urllib3

# SSL warnings disable (Mac fix)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(layout="wide")

st.title("⚡ BTC Institutional Dashboard (Working Version)")

# -------------------------
# SAFE REQUEST FUNCTION
# -------------------------

def fetch(url):

    try:

        r = requests.get(url, timeout=10, verify=False)

        if r.status_code == 200:

            return r.json()

    except Exception as e:

        st.warning(f"Error: {e}")

    return None


# -------------------------
# PRICE (3-level fallback)
# -------------------------

price = 0

# Try Futures
data = fetch("https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT")

if data:

    price = float(data["price"])

else:

    # Try Spot
    data = fetch("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")

    if data:

        price = float(data["price"])

    else:

        # Try CoinGecko
        data = fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")

        if data:

            price = data["bitcoin"]["usd"]


st.metric("BTC Price", price)


# -------------------------
# OPEN INTEREST
# -------------------------

oi = fetch("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT")

if oi:

    st.metric("Open Interest", float(oi["openInterest"]))


# -------------------------
# WHALE TRADES
# -------------------------

trades = fetch("https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=100")

if trades:

    df = pd.DataFrame(trades)

    df["price"] = df["price"].astype(float)
    df["qty"] = df["qty"].astype(float)

    whales = df[df.qty > 0.5]

    st.subheader("🐋 Whale Trades")

    st.dataframe(whales)


# -------------------------
# LIQUIDITY
# -------------------------

depth = fetch("https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=20")

if depth:

    bids = pd.DataFrame(depth["bids"], columns=["price","qty"]).astype(float)

    asks = pd.DataFrame(depth["asks"], columns=["price","qty"]).astype(float)

    fig = go.Figure()

    fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

    fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

    st.subheader("📚 Liquidity Heatmap")

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# EXPORT
# -------------------------

if trades:

    csv = df.to_csv(index=False).encode()

    st.download_button("Download CSV", csv, "btc_trades.csv")


# -------------------------
# REFRESH
# -------------------------

if st.button("Refresh"):

    st.rerun()
    
