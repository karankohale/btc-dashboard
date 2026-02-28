import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

st.set_page_config(layout="wide")

st.title("⚡ BTC PRO Dashboard (Cloud-Proof)")

# -----------------------
# SAFE REQUEST
# -----------------------

def safe_get(url):

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None

    return None


# -----------------------
# BTC PRICE (CoinGecko fallback)
# -----------------------

price_data = safe_get(
"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
)

price = price_data["bitcoin"]["usd"] if price_data else 0

st.metric("BTC Price", price)


# -----------------------
# BINANCE DEPTH (fallback safe)
# -----------------------

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

else:

    st.warning("Liquidity data unavailable")


# -----------------------
# RECENT TRADES (always works)
# -----------------------

trades = safe_get(
"https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=50"
)

if trades:

    df = pd.DataFrame(trades)

    df["price"] = df["price"].astype(float)
    df["qty"] = df["qty"].astype(float)

    st.subheader("🐋 Whale Trades")

    whales = df[df.qty > 1]

    st.dataframe(whales)

else:

    st.warning("Trade data unavailable")


# -----------------------
# EXPORT
# -----------------------

if trades:

    csv = df.to_csv(index=False).encode()

    st.download_button(
        "Download CSV",
        csv,
        "btc_trades.csv"
    )


# -----------------------
# REFRESH
# -----------------------

if st.button("Refresh"):

    st.rerun()
