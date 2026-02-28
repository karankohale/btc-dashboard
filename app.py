import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("💰 Smart Money Tracker Dashboard")

# -----------------------
# FUNCTION
# -----------------------

def get_data(url):

    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return None


# -----------------------
# PRICE
# -----------------------

price_data = get_data(
"https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
)

price = float(price_data["price"])

st.metric("BTC Price", price)


# -----------------------
# RECENT TRADES
# -----------------------

trades = get_data(
"https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=500"
)

df = pd.DataFrame(trades)

df["price"] = df["price"].astype(float)
df["qty"] = df["qty"].astype(float)

df["value"] = df["price"] * df["qty"]


# -----------------------
# WHALES
# -----------------------

whales = df[df["value"] > 50000]

st.subheader("🐋 Whale Trades")

st.dataframe(whales)


# -----------------------
# LIQUIDITY
# -----------------------

depth = get_data(
"https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=100"
)

bids = pd.DataFrame(depth["bids"], columns=["price","qty"]).astype(float)

asks = pd.DataFrame(depth["asks"], columns=["price","qty"]).astype(float)


# detect liquidity walls

support = bids.loc[bids.qty.idxmax()].price

resistance = asks.loc[asks.qty.idxmax()].price


col1, col2 = st.columns(2)

col1.metric("Support Zone", support)

col2.metric("Resistance Zone", resistance)


# -----------------------
# HEATMAP
# -----------------------

fig = go.Figure()

fig.add_bar(x=bids.price, y=bids.qty, name="Buy Liquidity")

fig.add_bar(x=asks.price, y=asks.qty, name="Sell Liquidity")

fig.add_vline(x=support)

fig.add_vline(x=resistance)

st.plotly_chart(fig, use_container_width=True)


# -----------------------
# SIGNAL
# -----------------------

if price < support:

    st.success("🟢 Smart Money BUY Zone")

elif price > resistance:

    st.error("🔴 Smart Money SELL Zone")

else:

    st.warning("⚠️ Neutral Zone")


# -----------------------
# EXPORT
# -----------------------

csv = whales.to_csv(index=False).encode()

st.download_button(

"Download Whale Data",

csv,

"whales.csv"
)
