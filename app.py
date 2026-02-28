import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(layout="wide")

# -----------------------------
# THEME
# -----------------------------

theme = st.sidebar.selectbox("Theme", ["Dark", "Light"])

bg = "#0e1117" if theme == "Dark" else "white"
text = "white" if theme == "Dark" else "black"

st.markdown(f"""
<style>
.stApp {{
background-color: {bg};
color: {text};
}}
</style>
""", unsafe_allow_html=True)

st.title("⚡ PRO BTC Futures Dashboard (Cloud Version)")

BASE = "https://fapi.binance.com/fapi/v1"

# -----------------------------
# SAFE API FUNCTION
# -----------------------------

def safe_get(url):

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass

    return None


# -----------------------------
# OPEN INTEREST
# -----------------------------

oi = safe_get(f"{BASE}/openInterest?symbol=BTCUSDT")

open_interest = float(oi["openInterest"]) if oi else 0


# -----------------------------
# FUNDING RATE
# -----------------------------

fund = safe_get(f"{BASE}/fundingRate?symbol=BTCUSDT&limit=1")

funding_rate = float(fund[0]["fundingRate"]) if fund else 0


# -----------------------------
# LIQUIDATIONS HISTORY
# -----------------------------

liq = safe_get(f"{BASE}/allForceOrders?symbol=BTCUSDT&limit=100")

if liq:

    liq_df = pd.DataFrame(liq)

    liq_df["price"] = liq_df["price"].astype(float)
    liq_df["qty"] = liq_df["origQty"].astype(float)

else:

    liq_df = pd.DataFrame()


# -----------------------------
# WHALE TRADES
# -----------------------------

trades = safe_get(f"{BASE}/aggTrades?symbol=BTCUSDT&limit=200")

if trades:

    trade_df = pd.DataFrame(trades)

    trade_df["price"] = trade_df["p"].astype(float)
    trade_df["qty"] = trade_df["q"].astype(float)

    whales = trade_df[trade_df.qty > 5]

else:

    trade_df = pd.DataFrame()
    whales = pd.DataFrame()


# -----------------------------
# LIQUIDITY HEATMAP
# -----------------------------

depth = safe_get(f"{BASE}/depth?symbol=BTCUSDT&limit=50")

if depth:

    bids = pd.DataFrame(depth["bids"], columns=["price", "qty"]).astype(float)

    asks = pd.DataFrame(depth["asks"], columns=["price", "qty"]).astype(float)

else:

    bids = pd.DataFrame()
    asks = pd.DataFrame()


# -----------------------------
# METRICS DISPLAY
# -----------------------------

c1, c2 = st.columns(2)

c1.metric("Open Interest", round(open_interest, 2))

c2.metric("Funding Rate", funding_rate)


# -----------------------------
# LIQUIDATIONS
# -----------------------------

st.subheader("🔥 Liquidations")

st.dataframe(liq_df)


# -----------------------------
# WHALES
# -----------------------------

st.subheader("🐋 Whale Trades")

st.dataframe(whales)


# -----------------------------
# LIQUIDITY HEATMAP
# -----------------------------

st.subheader("📚 Liquidity Heatmap")

fig = go.Figure()

if not bids.empty:
    fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

if not asks.empty:
    fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# EXPORT CSV
# -----------------------------

if not liq_df.empty:

    csv = liq_df.to_csv(index=False).encode()

    st.download_button(
        "Download Liquidations CSV",
        csv,
        "liquidations.csv"
    )


# -----------------------------
# REFRESH BUTTON
# -----------------------------

if st.button("🔄 Refresh Data"):

    st.rerun()
