import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime as dt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.ui import *

setup("Home", "🏠")
R_ = get_results()
ensure()

st.markdown(hero("SM Energy: live market and model dashboard",
                 "Compare Yahoo Finance market data with the assignment Heston/Asian-pricing model. Parameters remain editable and all responses include risk context.",
                 ["Live Yahoo Finance", "5-second refresh", "Interactive Heston", "AI guidance", "Assignment deliverables"]), unsafe_allow_html=True)

controls, data_controls = st.columns([1.25, 1])
with data_controls:
    st.subheader("Live market controls")
    ticker = st.text_input("Yahoo Finance ticker", value="SM", max_chars=12).strip().upper() or "SM"
    refresh_seconds = st.number_input("Refresh interval (seconds)", min_value=5, max_value=3600, value=5, step=5)

@st.fragment(run_every=refresh_seconds)
def market_strip(ticker):
    try:
        context = ld.market_snapshot(ticker)
        cols = st.columns(4)
        cards = [
            (f"{ticker} spot", context["spot"], "Live/close price"),
            ("1-day change", f"{context['change_pct']:+.2f}%" if context['change_pct'] is not None else "N/A", "Latest session"),
            ("SPX", context["spx"], "Market benchmark"),
            ("VIX", context["vix"], "Market volatility"),
        ]
        for col, (label, value, detail) in zip(cols, cards):
            displayed = f"${value:.2f}" if isinstance(value, float) and label != "VIX" else (f"{value:.2f}" if isinstance(value, float) else str(value))
            col.metric(label, displayed, detail)
        st.caption(f"Last refreshed: {dt.datetime.now().strftime('%H:%M:%S')} · Source: Yahoo Finance via yfinance")
        st.session_state["home_live_context"] = context
    except Exception:
        st.warning("Live market data is temporarily unavailable. The assignment dataset remains available below.")

st.subheader("Side-by-side market view")
left, right = st.columns(2)
with left:
    st.markdown("### Live market situation")
    market_strip(ticker)

with right:
    st.markdown("### Interactive model situation")
    ensure()
    p = ss.p
    p_cols = st.columns(5)
    limits = [(1e-3, 1.0), (1e-2, 8.0), (1e-3, 1.0), (1e-2, 2.0), (-.99, .99)]
    new_p = tuple(p_cols[i].number_input(n, min_value=limits[i][0], max_value=limits[i][1],
                                        value=float(np.clip(p[i], *limits[i])), format="%.4f", key="home_"+n)
                  for i, n in enumerate(PN))
    ss.p = new_p

    ic = st.columns(3)
    spot = ic[0].number_input("Spot", 1.0, 5000.0, float(ld.safe_spot(ticker)), key="home_spot")
    days = ic[1].number_input("Horizon (days)", 1, 750, 20, key="home_days")
    rate = ic[2].number_input("Risk-free rate", -0.05, 0.25, R_DEMO, format="%.4f", key="home_rate")
    T = days / 250

    with heavy("home simulation"):
        vanilla = float(model_price(spot, spot, T, rate, 0.0, new_p, "C")[0])
        asian, se, ci = asian_call_qe(spot, spot, T, rate, 0.0, new_p, int(days), mc_paths(100_000, int(days)))

    st.metric("ATM Asian call — fair", f"${asian:.4f}", f"95% CI [${ci[0]:.2f}, ${ci[1]:.2f}]")
    st.metric("ATM Asian call — client", f"${asian*1.04:.4f}", "4% fee")
    ss.last = {"ticker": ticker, "spot": spot, "days": days, "rate": rate,
               "vanilla": vanilla, "asian": asian, "fee_client": asian*1.04,
               "confidence_95": ci}

st.divider()
st.subheader("Audience guidance")
audience = st.segmented_control("Recommendation audience", ["Retail investor", "Investor", "Company"], default="Investor")
context = ss.get("home_live_context", {})
market_signal = "No live quote available"
if context:
    market_signal = "Live quote available" if context.get("spot") is not None else "Live quote unavailable"

if audience == "Retail investor":
    guidance = "Consider whether averaging over 20–750 days matches the retail objective. Compare the Asian price with a vanilla call, size positions conservatively, and do not treat model output as a buy/sell signal."
elif audience == "Company":
    guidance = "Use the model for treasury scenario planning and hedge-structure comparison. Validate liquidity, counterparty exposure, transaction costs, and hedge ratios before implementation."
else:
    guidance = "Review the model price, confidence interval, live market context, and assumptions together. The asymmetric parameters and weakly identified Heston coefficients require stress testing."

st.info(f"**{audience}:** {guidance}\n\n**Market status:** {market_signal}. The live and model panels use independently sourced inputs and must not be interpreted as forecasts.")

st.divider()
st.subheader("AI market assistant + disclaimer")
st.warning(DISC)
if not AI_ON():
    st.info("AI is in standby mode. Configure OPENROUTER_API_KEY and the Baidu ERNIE model in Streamlit secrets to activate it. No key is stored in this project.")
else:
    ai_panel("Home", {"last": ss.get("last")}, [
        "Analyse the live market situation and the model output",
        "Give separate guidance for retail, investor and company users",
        "What are the three biggest risks in today's result?",
    ])

st.divider()
st.subheader("Assignment results")
s1, s2, s3 = R_["step1c"], R_["step2c"], R_["step3b"]
put = s2["models"][s2["headline"]]["mc"]
mc = st.columns(4)
for col, (label, value, detail) in zip(mc, [
    ("Asian call fair", f"${s1['qe']['price']:.2f}", "20-day ATM Heston/Monte Carlo"),
    ("Asian call client", f"${s1['qe']['client']:.2f}", "Includes 4% fee"),
    (f"Put 70d K=${s2['K']:.2f}", f"${put['client']:.2f}", "Client price"),
    ("12M Euribor in 1y", f"{s3['expected']:.2%}", "CIR expected scenario"),
]):
    col.metric(label, value, detail)

st.caption("Research and education only — not financial, investment, legal or professional advice.")
