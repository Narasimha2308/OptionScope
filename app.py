import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import yfinance as yf
import numpy as np
import math
from datetime import datetime, date, timedelta
from streamlit_autorefresh import st_autorefresh

from database import (
    create_table,
    add_position,
    get_positions,
    update_position,
    delete_position
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="OptionScope",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=10000, key="marketrefresh")

# =========================================================
# LOT SIZES
# =========================================================

LOT_SIZES = {
    "NIFTY": 65,
    "BANKNIFTY": 30,
    "FINNIFTY": 40,
    "MIDCPNIFTY": 75,
    "SENSEX": 20
}

# =========================================================
# DATABASE
# =========================================================

create_table()

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp {
    background: linear-gradient(135deg, #060b14 0%, #0d1526 50%, #111f35 100%);
    color: white;
}

html, body, [class*="css"] {
    font-size: 15px !important;
}

body, p, span, div, label, input, textarea, select, button {
    font-family: 'Space Grotesk', sans-serif !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #030810 0%, #0a1120 100%);
    border-right: 1px solid #1e3a5f;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.main-title {
    font-size: 34px;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    font-size: 13px;
    color: #94a3b8;
    letter-spacing: 2px;
    margin-top: -5px;
    margin-bottom: 20px;
}

div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0d1b2e, #142233);
    border: 1px solid #1e3a5f;
    padding: 12px;
    border-radius: 14px;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0ea5e9, #4f46e5);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px;
    font-weight: 600;
}

.stButton > button:hover {
    transform: translateY(-1px);
}

.stTextInput input,
.stNumberInput input,
textarea {
    background-color: #0d1b2e !important;
    color: white !important;
    border: 1px solid #1e3a5f !important;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #0d1b2e !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1e3a5f;
    border-radius: 12px;
}

.greek-box {
    background: linear-gradient(145deg, #0d1b2e, #111f35);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
}

.greek-label {
    font-size: 12px;
    color: #94a3b8;
    text-transform: uppercase;
}

.greek-value {
    font-size: 20px;
    font-weight: 700;
    color: #38bdf8;
    margin-top: 5px;
    font-family: 'JetBrains Mono', monospace;
}

.risk-card {
    background: linear-gradient(145deg, #0d1b2e, #142233);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LIVE PRICE
# =========================================================

@st.cache_data(ttl=15)
def get_live_price(symbol: str):

    mapping = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
        "MIDCPNIFTY": "^NSEMDCP50",
        "SENSEX": "^BSESN"
    }

    try:
        data = yf.Ticker(mapping[symbol]).history(period="2d")

        if data.empty:
            return None, None

        current = round(float(data["Close"].iloc[-1]), 2)

        if len(data) > 1:
            prev = round(float(data["Close"].iloc[-2]), 2)
        else:
            prev = current

        return current, round(current - prev, 2)

    except Exception:
        return None, None

# =========================================================
# BLACK SCHOLES
# =========================================================

def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def norm_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)

def black_scholes_greeks(S, K, T, r, sigma, option_type="CE"):

    if T <= 0 or S <= 0 or K <= 0 or sigma <= 0:
        return {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0,
            "price": 0
        }

    try:

        d1 = (
            math.log(S / K) +
            (r + 0.5 * sigma**2) * T
        ) / (sigma * math.sqrt(T))

        d2 = d1 - sigma * math.sqrt(T)

        gamma = norm_pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * norm_pdf(d1) * math.sqrt(T) / 100

        if option_type == "CE":

            delta = norm_cdf(d1)

            price = (
                S * norm_cdf(d1)
                - K * math.exp(-r * T) * norm_cdf(d2)
            )

            theta = (
                -(S * norm_pdf(d1) * sigma) /
                (2 * math.sqrt(T))
                - r * K * math.exp(-r * T) * norm_cdf(d2)
            ) / 365

        else:

            delta = norm_cdf(d1) - 1

            price = (
                K * math.exp(-r * T) * norm_cdf(-d2)
                - S * norm_cdf(-d1)
            )

            theta = (
                -(S * norm_pdf(d1) * sigma) /
                (2 * math.sqrt(T))
                + r * K * math.exp(-r * T) * norm_cdf(-d2)
            ) / 365

        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
            "price": round(price, 2)
        }

    except Exception:

        return {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0,
            "price": 0
        }

# =========================================================
# SUMMARY
# =========================================================

@st.cache_data(ttl=30)
def compute_summary(data_tuple):

    if not data_tuple:
        return {
            "df": pd.DataFrame(),
            "total_pnl": 0,
            "win_rate": 0,
            "winning": 0,
            "losing": 0,
            "open_count": 0,
            "closed_count": 0,
            "best": 0,
            "worst": 0,
            "avg": 0,
            "exposure": 0
        }

    df = pd.DataFrame(list(data_tuple), columns=[
        "ID",
        "Symbol",
        "Strike",
        "Option Type",
        "Side",
        "Broker",
        "Strategy",
        "Quantity",
        "Premium",
        "Current Premium",
        "Expiry",
        "Notes",
        "Status",
        "Created At"
    ])

    df["Created At"] = pd.to_datetime(
        df["Created At"],
        errors="coerce"
    )

    df["P&L"] = (
        (df["Current Premium"] - df["Premium"])
        * df["Quantity"]
    )

    df.loc[df["Side"] == "SELL", "P&L"] *= -1

    df["P&L %"] = (
        df["P&L"] /
        (df["Premium"] * df["Quantity"])
    ) * 100

    df["P&L %"] = df["P&L %"].round(2)

    df["Breakeven"] = np.where(
        df["Option Type"] == "CE",
        df["Strike"] + df["Premium"],
        df["Strike"] - df["Premium"]
    )

    df["Max Loss"] = np.where(
        df["Side"] == "BUY",
        df["Premium"] * df["Quantity"],
        df["Strike"] * df["Quantity"] * 0.20
    )

    df["Risk Type"] = np.where(
        df["Side"] == "BUY",
        "Defined",
        "Naked"
    )

    winning = int((df["P&L"] > 0).sum())
    losing = int((df["P&L"] < 0).sum())

    total = len(df)

    win_rate = (
        winning / total * 100
        if total > 0 else 0
    )

    return {
        "df": df,
        "total_pnl": float(df["P&L"].sum()),
        "win_rate": win_rate,
        "winning": winning,
        "losing": losing,
        "open_count": int((df["Status"] == "OPEN").sum()),
        "closed_count": int((df["Status"] == "CLOSED").sum()),
        "best": float(df["P&L"].max()),
        "worst": float(df["P&L"].min()),
        "avg": float(df["P&L"].mean()),
        "exposure": float(
            (df["Premium"] * df["Quantity"]).sum()
        )
    }

# =========================================================
# EXPIRY
# =========================================================

def get_upcoming_expiries(symbol, n=6):

    expiries = []
    today = date.today()

    if symbol == "NIFTY":
        weekday = 1

    elif symbol == "SENSEX":
        weekday = 3

    else:
        weekday = 1

    d = today

    while len(expiries) < n:

        if d.weekday() == weekday:
            expiries.append(d)

        d += timedelta(days=1)

    return expiries

# =========================================================
# TITLE
# =========================================================

title_col, refresh_col = st.columns([5, 1])

with title_col:
    st.markdown(
        '<div class="main-title">📈 OptionScope</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Professional Options Dashboard</div>',
        unsafe_allow_html=True
    )

with refresh_col:

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

# =========================================================
# LIVE MARKET
# =========================================================

st.header("📡 Live Market")

m1, m2, m3, m4 = st.columns(4)

for col, sym in zip(
    [m1, m2, m3, m4],
    ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"]
):

    price, change = get_live_price(sym)

    col.metric(
        sym,
        f"{price:,.2f}" if price else "N/A",
        f"{change:+.2f}" if change is not None else None
    )

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## ➕ Add Position")

symbol = st.sidebar.selectbox(
    "Symbol",
    list(LOT_SIZES.keys())
)

strike = st.sidebar.number_input(
    "Strike Price",
    min_value=0.0,
    step=50.0
)

option_type = st.sidebar.selectbox(
    "Option Type",
    ["CE", "PE"]
)

side = st.sidebar.selectbox(
    "Side",
    ["BUY", "SELL"]
)

broker = st.sidebar.selectbox(
    "Broker",
    [
        "Zerodha",
        "Groww",
        "Angel One",
        "Upstox",
        "Dhan",
        "Fyers"
    ]
)

strategy = st.sidebar.selectbox(
    "Strategy",
    [
        "Scalping",
        "Intraday",
        "Swing",
        "BTST",
        "Positional",
        "Iron Condor",
        "Straddle",
        "Strangle"
    ]
)

lots = st.sidebar.number_input(
    "Lots",
    min_value=1,
    step=1
)

quantity = lots * LOT_SIZES[symbol]

st.sidebar.info(
    f"Lot Size: {LOT_SIZES[symbol]} | Qty: {quantity}"
)

premium = st.sidebar.number_input(
    "Entry Premium",
    min_value=0.0,
    step=0.5
)

current_premium = st.sidebar.number_input(
    "Current Premium",
    min_value=0.0,
    step=0.5
)

notes = st.sidebar.text_area("Trade Notes")

expiry_options = [
    e.strftime("%d %b %Y")
    for e in get_upcoming_expiries(symbol)
]

expiry_label = st.sidebar.selectbox(
    "Expiry",
    expiry_options
)

expiry_date = datetime.strptime(
    expiry_label,
    "%d %b %Y"
).date()

if st.sidebar.button("✅ Add Position"):

    add_position(
        symbol,
        strike,
        option_type,
        side,
        broker,
        strategy,
        quantity,
        premium,
        current_premium,
        expiry_date.strftime("%d-%m-%Y"),
        notes,
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    )

    st.success("Position Added Successfully")

    st.cache_data.clear()

    st.rerun()

# =========================================================
# MANAGE POSITIONS
# =========================================================

positions = get_positions()

if positions:

    ids = [p[0] for p in positions]

    st.sidebar.markdown("---")
    st.sidebar.markdown("## ✏️ Update Premium")

    update_id = st.sidebar.selectbox(
        "Position ID",
        ids
    )

    updated_premium = st.sidebar.number_input(
        "New Premium",
        min_value=0.0,
        step=0.5,
        key="upd"
    )

    if st.sidebar.button("Update"):

        update_position(
            update_id,
            updated_premium
        )

        st.success("Updated")

        st.cache_data.clear()

        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🗑 Delete Position")

    delete_id = st.sidebar.selectbox(
        "Delete ID",
        ids,
        key="del"
    )

    if st.sidebar.button("Delete"):

        delete_position(delete_id)

        st.success("Deleted")

        st.cache_data.clear()

        st.rerun()

# =========================================================
# LOAD DATA
# =========================================================

raw = get_positions()

key = tuple(tuple(r) for r in raw)

summary = compute_summary(key)

df = summary["df"]

# =========================================================
# METRICS
# =========================================================

st.markdown("---")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Positions", len(df))
c2.metric("Open", summary["open_count"])
c3.metric("Closed", summary["closed_count"])
c4.metric("Exposure", f"₹{summary['exposure']:,.0f}")
c5.metric("Net P&L", f"₹{summary['total_pnl']:,.0f}")
c6.metric("Win Rate", f"{summary['win_rate']:.1f}%")

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Positions",
    "📈 Analytics",
    "🔢 Greeks",
    "🛡 Risk"
])

# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.header("📋 Positions")

    if not df.empty:

        st.dataframe(
            df,
            use_container_width=True
        )

        st.download_button(
            "📥 Export CSV",
            df.to_csv(index=False),
            file_name="optionscope.csv",
            mime="text/csv"
        )

    else:
        st.info("No positions added")

# =========================================================
# TAB 2
# =========================================================

with tab2:

    if not df.empty:

        st.header("📈 Strategy Performance")

        strat = (
            df.groupby("Strategy")["P&L"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            strat,
            x="Strategy",
            y="P&L",
            color="P&L",
            title="Strategy P&L"
        )

        fig.update_layout(
            paper_bgcolor="#0d1b2e",
            plot_bgcolor="#0d1b2e",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.header("📈 Equity Curve")

        eq = df.sort_values("Created At").copy()

        eq["Cumulative"] = eq["P&L"].cumsum()

        fig2 = px.area(
            eq,
            x="Created At",
            y="Cumulative"
        )

        fig2.update_layout(
            paper_bgcolor="#0d1b2e",
            plot_bgcolor="#0d1b2e",
            font_color="white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# =========================================================
# TAB 3
# =========================================================

with tab3:

    st.header("🔢 Greeks Calculator")

    col1, col2 = st.columns(2)

    with col1:

        g_spot = st.number_input(
            "Spot Price",
            value=22000.0
        )

        g_strike = st.number_input(
            "Strike Price",
            value=22000.0
        )

        g_type = st.selectbox(
            "Option Type",
            ["CE", "PE"]
        )

    with col2:

        g_days = st.number_input(
            "Days to Expiry",
            value=7
        )

        g_iv = st.slider(
            "IV %",
            5,
            100,
            15
        )

        g_rf = st.number_input(
            "Risk Free Rate",
            value=6.5
        )

    if st.button("⚡ Calculate Greeks"):

        T = g_days / 365

        greeks = black_scholes_greeks(
            g_spot,
            g_strike,
            T,
            g_rf / 100,
            g_iv / 100,
            g_type
        )

        labels = [
            "Delta",
            "Gamma",
            "Theta",
            "Vega",
            "Price"
        ]

        keys = [
            "delta",
            "gamma",
            "theta",
            "vega",
            "price"
        ]

        cols = st.columns(5)

        for col, label, key in zip(cols, labels, keys):

            with col:

                st.markdown(f"""
                <div class="greek-box">
                    <div class="greek-label">{label}</div>
                    <div class="greek-value">{greeks[key]}</div>
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# TAB 4
# =========================================================

with tab4:

    st.header("🛡 Risk Manager")

    if not df.empty:

        total_loss = df["Max Loss"].sum()

        rr_ratio = (
            abs(summary["best"] / summary["worst"])
            if summary["worst"] != 0 else 0
        )

        exposure_pct = (
            summary["exposure"] / 500000
        ) * 100

        r1, r2, r3 = st.columns(3)

        with r1:

            st.markdown(f"""
            <div class="risk-card">
                <h3>Max Loss</h3>
                <h2 style="color:#ef4444;">
                ₹{total_loss:,.0f}
                </h2>
            </div>
            """, unsafe_allow_html=True)

        with r2:

            st.markdown(f"""
            <div class="risk-card">
                <h3>Risk Reward</h3>
                <h2 style="color:#22c55e;">
                1 : {rr_ratio:.2f}
                </h2>
            </div>
            """, unsafe_allow_html=True)

        with r3:

            st.markdown(f"""
            <div class="risk-card">
                <h3>Capital Used</h3>
                <h2 style="color:#38bdf8;">
                {exposure_pct:.1f}%
                </h2>
            </div>
            """, unsafe_allow_html=True)

    else:

        st.info("No positions available")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

if summary["total_pnl"] > 0:

    st.success(
        f"🟢 Profit ₹{summary['total_pnl']:,.2f}"
    )

elif summary["total_pnl"] < 0:

    st.error(
        f"🔴 Loss ₹{summary['total_pnl']:,.2f}"
    )

else:

    st.info("No P&L yet")