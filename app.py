import streamlit as st
import websocket
import json
import threading
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

# --------------------
# CONFIG
# --------------------

st.set_page_config(layout="wide")

# --------------------
# THEME
# --------------------

theme = st.sidebar.selectbox("Theme", ["Dark","Light"])

if theme=="Dark":

    bg="#0e1117"
    text="white"

else:

    bg="white"
    text="black"


st.markdown(f"""
<style>
.stApp {{
background-color:{bg};
color:{text};
}}
</style>
""", unsafe_allow_html=True)


st.title("ULTIMATE Institutional BTC Dashboard")


# --------------------
# STATE
# --------------------

if "init" not in st.session_state:

    st.session_state.init=True

    st.session_state.price=0

    st.session_state.buy=0
    st.session_state.sell=0
    st.session_state.cvd=0

    st.session_state.trades=[]

    st.session_state.bids=[]
    st.session_state.asks=[]

    st.session_state.whales=[]

    st.session_state.orderblocks=[]


# --------------------
# TRADE STREAM
# --------------------

def trades_ws():

    def on_msg(ws,msg):

        d=json.loads(msg)

        price=float(d["p"])
        qty=float(d["q"])

        st.session_state.price=price

        side="BUY"

        if d["m"]:

            st.session_state.sell+=qty
            st.session_state.cvd-=qty

            side="SELL"

        else:

            st.session_state.buy+=qty
            st.session_state.cvd+=qty


        trade=[

        datetime.now(),

        price,

        qty,

        side

        ]

        st.session_state.trades.append(trade)


        if qty>1:

            st.session_state.whales.append(trade)


        if qty>0.8:

            st.session_state.orderblocks.append(trade)


    ws=websocket.WebSocketApp(

    "wss://stream.binance.com:9443/ws/btcusdt@trade",

    on_message=on_msg

    )

    ws.run_forever()



# --------------------
# ORDER BOOK STREAM
# --------------------

def depth_ws():

    def on_msg(ws,msg):

        d=json.loads(msg)

        st.session_state.bids=d["b"]

        st.session_state.asks=d["a"]


    ws=websocket.WebSocketApp(

    "wss://stream.binance.com:9443/ws/btcusdt@depth10@100ms",

    on_message=on_msg

    )

    ws.run_forever()



threading.Thread(target=trades_ws,daemon=True).start()

threading.Thread(target=depth_ws,daemon=True).start()



# --------------------
# CALCULATIONS
# --------------------

total=st.session_state.buy+st.session_state.sell

buy_per=(st.session_state.buy/total*100) if total>0 else 0


# --------------------
# METRICS
# --------------------

c1,c2,c3,c4=st.columns(4)

c1.metric("Price", st.session_state.price)

c2.metric("Buy %", round(buy_per,2))

c3.metric("Sell %", round(100-buy_per,2))

c4.metric("CVD", round(st.session_state.cvd,2))


# --------------------
# LIQUIDITY HEATMAP
# --------------------

st.subheader("Liquidity Heatmap")

bids=pd.DataFrame(

st.session_state.bids,

columns=["Price","Volume"]

)

asks=pd.DataFrame(

st.session_state.asks,

columns=["Price","Volume"]

)

bids["Price"]=bids["Price"].astype(float)

bids["Volume"]=bids["Volume"].astype(float)

asks["Price"]=asks["Price"].astype(float)

asks["Volume"]=asks["Volume"].astype(float)


fig=go.Figure()

fig.add_trace(go.Bar(

x=bids["Price"],

y=bids["Volume"],

name="Bids"

))

fig.add_trace(go.Bar(

x=asks["Price"],

y=asks["Volume"],

name="Asks"

))

st.plotly_chart(fig,use_container_width=True)


# --------------------
# ORDER BLOCKS
# --------------------

st.subheader("Order Blocks")

st.dataframe(

pd.DataFrame(

st.session_state.orderblocks,

columns=["Time","Price","Qty","Side"]

)

)


# --------------------
# WHALES
# --------------------

st.subheader("Whales")

st.dataframe(

pd.DataFrame(

st.session_state.whales,

columns=["Time","Price","Qty","Side"]

)

)


# --------------------
# TRADES
# --------------------

st.subheader("Trades")

df=pd.DataFrame(

st.session_state.trades,

columns=["Time","Price","Qty","Side"]

)

st.dataframe(df)


# --------------------
# EXPORT
# --------------------

csv=df.to_csv(index=False).encode()

st.download_button(

"Export CSV",

csv,

"btc_trades.csv",

"text/csv"

)


# --------------------

time.sleep(2)

st.rerun()
