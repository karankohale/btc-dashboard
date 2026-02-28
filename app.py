import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
from datetime import datetime

st.set_page_config(layout="wide")

# ----------------
# THEME
# ----------------

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


st.title("ULTIMATE Institutional BTC Dashboard")


# ----------------
# FETCH DATA
# ----------------

@st.cache_data(ttl=2)

def get_price():

    url="https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

    return float(requests.get(url).json()["price"])


@st.cache_data(ttl=2)

def get_trades():

    url="https://api.binance.com/api/v3/trades?symbol=BTCUSDT&limit=100"

    data=requests.get(url).json()

    df=pd.DataFrame(data)

    df["price"]=df["price"].astype(float)

    df["qty"]=df["qty"].astype(float)

    df["time"]=pd.to_datetime(df["time"], unit="ms")

    df["side"]=df["isBuyerMaker"].apply(

        lambda x:"SELL" if x else "BUY"

    )

    return df


@st.cache_data(ttl=2)

def get_depth():

    url="https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=10"

    data=requests.get(url).json()

    bids=pd.DataFrame(data["bids"], columns=["price","qty"])

    asks=pd.DataFrame(data["asks"], columns=["price","qty"])

    bids=bids.astype(float)

    asks=asks.astype(float)

    return bids, asks


price=get_price()

trades=get_trades()

bids, asks=get_depth()


# ----------------
# CALCULATIONS
# ----------------

buy=trades[trades.side=="BUY"].qty.sum()

sell=trades[trades.side=="SELL"].qty.sum()

total=buy+sell

buy_per=(buy/total*100) if total>0 else 0

cvd=buy-sell


# ----------------
# METRICS
# ----------------

c1,c2,c3,c4=st.columns(4)

c1.metric("Price", price)

c2.metric("Buy %", round(buy_per,2))

c3.metric("Sell %", round(100-buy_per,2))

c4.metric("CVD", round(cvd,2))


# ----------------
# HEATMAP
# ----------------

st.subheader("Liquidity Heatmap")

fig=go.Figure()

fig.add_bar(x=bids.price, y=bids.qty, name="Bids")

fig.add_bar(x=asks.price, y=asks.qty, name="Asks")

st.plotly_chart(fig, use_container_width=True)


# ----------------
# ORDERBLOCK
# ----------------

st.subheader("Order Blocks")

orderblocks=trades[trades.qty>0.5]

st.dataframe(orderblocks)


# ----------------
# WHALES
# ----------------

st.subheader("Whales")

whales=trades[trades.qty>1]

st.dataframe(whales)


# ----------------
# TRADES
# ----------------

st.subheader("Trades")

st.dataframe(trades)


# ----------------
# EXPORT
# ----------------

csv=trades.to_csv(index=False).encode()

st.download_button(

"Export CSV",

csv,

"btc_trades.csv",

"text/csv"

)


time.sleep(2)

st.rerun()
