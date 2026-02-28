import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("💰 Smart Money Tracker PRO")

# -----------------------
# SAFE FETCH
# -----------------------

def fetch(url):

    try:

        r = requests.get(url, timeout=10)

        if r.status_code == 200:

            return r.json()

    except:

        return None

    return None


# -----------------------
# PRICE
# -----------------------

price = None

binance = fetch(
"https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
)

if binance and "price" in binance:

    price = float(binance["price"])

else:

    cg = fetch(
"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
)

    if cg:

        price = cg["bitcoin"]["usd"]


st.metric("BTC Price", price)


# -----------------------
# TRADES
# -----------------------

trade_data = fetch(
"https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=500"
)

support = None
resistance = None

if trade_data:

    df = pd.DataFrame(trade_data)

    df["price"] = df["price"].astype(float)

    df["qty"] = df["qty"].astype(float)

    df["value"] = df["price"] * df["qty"]

    whales = df[df.value > 50000]

    st.subheader("🐋 Whale Activity")

    st.dataframe(whales)

else:

    st.warning("Trade data unavailable")


# -----------------------
# LIQUIDITY
# -----------------------

depth = fetch(
"https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=100"
)

if depth:

    bids = pd.DataFrame(depth["bids"], columns=["price","qty"]).astype(float)

    asks = pd.DataFrame(depth["asks"], columns=["price","qty"]).astype(float)

    support = bids.loc[bids.qty.idxmax()].price

    resistance = asks.loc[asks.qty.idxmax()].price


    col1, col2 = st.columns(2)

    col1.metric("Support", support)

    col2.metric("Resistance", resistance)


    fig = go.Figure()

    fig.add_bar(x=bids.price, y=bids.qty, name="Buy Liquidity")

    fig.add_bar(x=asks.price, y=asks.qty, name="Sell Liquidity")

    fig.add_vline(x=support)

    fig.add_vline(x=resistance)

    st.subheader("Liquidity Heatmap")

    st.plotly_chart(fig, use_container_width=True)

else:

    st.warning("Liquidity unavailable")


# -----------------------
# SIGNAL ENGINE (PRO)
# -----------------------

st.subheader("Smart Money Signal")

if price and support and resistance:

    if price < support:

        st.success("🟢 STRONG BUY ZONE")

    elif price > resistance:

        st.error("🔴 STRONG SELL ZONE")

    else:

        st.info("⚪ ACCUMULATION ZONE")

else:

    st.warning("Signal unavailable")


# -----------------------
# REFRESH
# -----------------------

if st.button("Refresh"):

    st.rerun()
