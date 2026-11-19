import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import *
setup("Real-Time Data", "📡")
st.title("Real-Time Market Data")

st.caption("Yahoo Finance data is delayed where applicable. Refresh frequency can be set below.")
refresh = st.number_input("Refresh interval (seconds)", min_value=5, max_value=3600, value=5, step=5)

auto_refresh = st.toggle("Enable live refresh", value=True)

@st.fragment(run_every=refresh if auto_refresh else None)
def live_dashboard():
    ticker = st.text_input("Ticker", value="SM", max_chars=12, key="rt_ticker").strip().upper() or "SM"
    try:
        snapshot = ld.market_snapshot(ticker)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"{ticker} spot", f"${snapshot['spot']:,.2f}" if snapshot["spot"] is not None else "N/A")
        c2.metric("Change", f"{snapshot['change_pct']:+.2f}%" if snapshot["change_pct"] is not None else "N/A")
        c3.metric("SPX", f"{snapshot['spx']:,.2f}" if snapshot["spx"] is not None else "N/A")
        c4.metric("VIX", f"{snapshot['vix']:,.2f}" if snapshot["vix"] is not None else "N/A")
        st.caption(f"Yahoo Finance snapshot at {snapshot['timestamp']} UTC")

        st.subheader("Option chain")
        expiries = ld.expiries(ticker)
        if expiries:
            expiry = st.selectbox("Expiry", expiries)
            chain = ld.chain(expiry, ticker)
            st.dataframe(chain, hide_index=True, use_container_width=True)
        else:
            st.info("No option expiries are currently returned for this ticker.")

        st.subheader("Market headlines")
        st.dataframe(pd.DataFrame(ld.news(ticker)), hide_index=True, use_container_width=True)
    except Exception as exc:
        st.warning("Live data is currently unavailable. The assignment dashboard still uses the supplied data.")
        st.caption(type(exc).__name__)

live_dashboard()
st.warning(DISC)
if AI_ON():
    ai_panel("Real-Time Data", {"live_context": ss.get("home_live_context")}, [
        "Analyse this market snapshot",
        "How should an investor interpret VIX and SPX?",
        "What risks affect the SM option model?",
    ])
