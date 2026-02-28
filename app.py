import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

st.set_page_config(layout="wide")

st.title("⚡ BTC Liquidation Dashboard (Cloud Compatible)")


# -------------------------
# SAFE API CALL
# -------------------------

def safe_get(url):

    try:

        r = requests.get(url, timeout=10)

        if r.status_code == 200:

            return r.json()

    except:

        return None


# -------------------------
# LIQUIDATIONS
# -------------------------

liq_data = safe_get(

"https://fapi.binance.com/fapi/v1/forceOrders?symbol=BTCUSDT&limit=50"

)

if liq_data:

    liq_df = pd.DataFrame(liq_data)

    liq_df["price"] = liq_df["price"].astype(float)

    liq_df["qty"] = liq_df["origQty"].astype(float)

else:

    liq_df = pd.DataFrame()


st.subheader("🔥 Liquidations")

st.dataframe(liq_df)


# -------------------------
# TRADES
# -------------------------

trade_data = safe_get(

"https://fapi.binance.com/fapi/v1/trades?symbol=BTCUSDT&limit=100"

)

if trade_data:

    trade_df = pd.DataFrame(trade_data)

    trade_df["price"] = trade_df["price"].astype(float)

    trade_df["qty"] = trade_df["qty"].astype(float)

else:

    trade_df = pd.DataFrame()


st.subheader("🐋 Whale Trades")

if not trade_df.empty:

    whales = trade_df[trade_df.qty > 5]

    st.dataframe(whales)


# -------------------------
# LIQUIDITY
# -------------------------

depth = safe_get(

"https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=20"

)

if depth:

    bids = pd.DataFrame(depth["bids"], columns=["price","qty"]).astype(float)

    asks = pd.DataFrame(depth["asks"], columns=["price","qty"]).astype(float)


    st.subheader("📚 Liquidity Heatmap")

    fig = go.Figure()

    fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

    fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# EXPORT
# -------------------------

if not liq_df.empty:

    csv = liq_df.to_csv(index=False).encode()

    st.download_button(

        "Download Liquidation CSV",

        csv,

        "liquidations.csv"

    )


# -------------------------
# REFRESH BUTTON
# -------------------------

if st.button("Refresh Data"):

    st.write("Refreshing...")

    time.sleep(1)

    st.rerun()
