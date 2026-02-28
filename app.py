import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

st.set_page_config(layout="wide")

st.title("⚡ BTC Futures Institutional Dashboard")

BASE = "https://fapi.binance.com/fapi/v1"


def get_json(url):

    return requests.get(url).json()


# -------------------------
# OPEN INTEREST
# -------------------------

oi = get_json(f"{BASE}/openInterest?symbol=BTCUSDT")

open_interest = float(oi["openInterest"])

st.metric("Open Interest", open_interest)


# -------------------------
# FUNDING
# -------------------------

fund = get_json(f"{BASE}/fundingRate?symbol=BTCUSDT&limit=1")

fund_rate = float(fund[0]["fundingRate"])

st.metric("Funding Rate", fund_rate)


# -------------------------
# LIQUIDATIONS
# -------------------------

liq = get_json(f"{BASE}/allForceOrders?symbol=BTCUSDT&limit=50")

liq_df = pd.DataFrame(liq)

liq_df["price"] = liq_df["price"].astype(float)

st.subheader("Liquidations")

st.dataframe(liq_df)


# -------------------------
# WHALES
# -------------------------

trades = get_json(f"{BASE}/aggTrades?symbol=BTCUSDT&limit=200")

df = pd.DataFrame(trades)

df["price"] = df["p"].astype(float)

df["qty"] = df["q"].astype(float)

whales = df[df.qty > 5]

st.subheader("Whales")

st.dataframe(whales)


# -------------------------
# LIQUIDITY
# -------------------------

depth = get_json(f"{BASE}/depth?symbol=BTCUSDT&limit=50")

bids = pd.DataFrame(depth["bids"], columns=["price","qty"]).astype(float)

asks = pd.DataFrame(depth["asks"], columns=["price","qty"]).astype(float)


fig = go.Figure()

fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

st.subheader("Liquidity")

st.plotly_chart(fig)


# -------------------------
# REFRESH LOOP
# -------------------------

time.sleep(3)

st.rerun()
