import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

st.set_page_config(layout="wide")

# ---------------- THEME ----------------

theme = st.sidebar.selectbox("Theme", ["Dark","Light"])

bg = "#0e1117" if theme=="Dark" else "white"
text = "white" if theme=="Dark" else "black"

st.markdown(f"""
<style>
.stApp {{
background-color:{bg};
color:{text};
}}
</style>
""", unsafe_allow_html=True)

st.title("BTC Institutional Dashboard")

# ---------------- AUTO REFRESH ----------------

st.autorefresh(interval=5000, key="refresh")

# ---------------- SAFE REQUEST ----------------

def safe_get(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# ✅ USE BINANCE US (NOT global)

BASE = "https://api.binance.us/api/v3"

# ---------------- PRICE ----------------

price_data = safe_get(f"{BASE}/ticker/price?symbol=BTCUSDT")

price = float(price_data["price"]) if price_data else 0

# ---------------- TRADES ----------------

trades_data = safe_get(f"{BASE}/trades?symbol=BTCUSDT&limit=50")

if trades_data:

    trades = pd.DataFrame(trades_data)

    trades["price"] = trades["price"].astype(float)
    trades["qty"] = trades["qty"].astype(float)
    trades["side"] = trades["isBuyerMaker"].apply(
        lambda x: "SELL" if x else "BUY"
    )

else:

    trades = pd.DataFrame()

# ---------------- DEPTH ----------------

depth = safe_get(f"{BASE}/depth?symbol=BTCUSDT&limit=10")

if depth:

    bids = pd.DataFrame(depth["bids"], columns=["price","qty"]).astype(float)
    asks = pd.DataFrame(depth["asks"], columns=["price","qty"]).astype(float)

else:

    bids = pd.DataFrame()
    asks = pd.DataFrame()

# ---------------- CALC ----------------

buy = trades[trades.side=="BUY"].qty.sum() if not trades.empty else 0
sell = trades[trades.side=="SELL"].qty.sum() if not trades.empty else 0

total = buy + sell
buy_per = (buy/total*100) if total>0 else 0
cvd = buy - sell

# ---------------- METRICS ----------------

c1,c2,c3,c4 = st.columns(4)

c1.metric("BTC Price", price)
c2.metric("Buy %", round(buy_per,2))
c3.metric("Sell %", round(100-buy_per,2))
c4.metric("CVD", round(cvd,2))

# ---------------- HEATMAP ----------------

st.subheader("Liquidity")

fig = go.Figure()

if not bids.empty:
    fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

if not asks.empty:
    fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

st.plotly_chart(fig, use_container_width=True)

# ---------------- TRADES ----------------

st.subheader("Trades")

st.dataframe(trades)

# ---------------- EXPORT ----------------

csv = trades.to_csv(index=False).encode()

st.download_button("Export CSV", csv, "btc.csv", "text/csv")
