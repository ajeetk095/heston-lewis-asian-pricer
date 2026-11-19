import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Real Time Data', '📡')
st.title("Real-Time Data"); auto = st.toggle("Auto-refresh every 60 s", False)
@st.fragment(run_every=60 if auto else None)
def live():
    try:
        s = ld.spot(); st.metric("SM spot (delayed)", f"${s:.2f}"); st.caption(f"Fetched/rendered {time.strftime('%H:%M:%S')} · cache TTLs: spot 60s, chain 5m, rates 1h")
        st.write("Context:", ld.market_context(), "| risk-free (FRED DGS3MO):", ld.risk_free(), "| div yield:", ld.dividend_yield())
        ex = st.selectbox("Expiry", ld.expiries()); ch = ld.chain(ex); st.dataframe(ch)
        if st.button("Calibrate on live chain"):
            T = max((pd.Timestamp(ex)-pd.Timestamp.today()).days,1)/365; dfl = ch.assign(**{'Days to maturity': 0})
            with heavy('calibration'): res = calibrate(dfl, s, ld.risk_free(), ld.dividend_yield(), T, maxiter=60); st.write(dict(zip(PN, np.round(res['params'],4))), "RMSE", res['rmse'])
        st.dataframe(pd.DataFrame(ld.news()))
    except Exception as e:
        st.warning(f"Live data is unavailable right now. **Demo mode** — assignment dataset, spot ${S_DEMO}, r={R_DEMO:.1%}."); st.dataframe(load_data(DATA_FILE, 15))
live()

ai_button("🤖 Market brief from live data", "Give a short market brief for SM Energy using the live data: spot, VIX/S&P/TNX context, risk-free rate, and what it implies for option pricing. State clearly if data is unavailable.", None, "Real Time Data")
ai_panel("Real Time Data", None, ["Is volatility high relative to the S&P/VIX?", "How does the risk-free rate affect my prices?", "What does the option chain imply about skew?"])
