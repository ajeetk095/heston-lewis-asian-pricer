import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import *

setup("Recommendations", "💡")
st.title("Recommendations")
st.caption("Illustrative scenario guidance only — not financial or investment advice.")
ensure()

r = ss.res
p = ss.p
v = float(lewis_call(S_DEMO, S_DEMO, 20/250, R_DEMO, 0.0, p)[0])
a, se, ci = asian_call_qe(S_DEMO, S_DEMO, 20/250, R_DEMO, 0.0, p, 20, 100_000)

st.warning(DISC)

audience = st.segmented_control("User type", ["Retail", "Investor", "Company"], default="Retail")

base = recommendations(S_DEMO, S_DEMO, 20/250, v, a, ci, r["rmse"], r["feller"], p)
for line in base:
    st.markdown("- " + line)

if audience == "Retail":
    st.subheader("Retail-user checklist")
    st.markdown("- Compare downside protection, premium cost and liquidity.\n- Use a small, position-sized allocation and a documented exit condition.\n- Prefer vanilla or simpler instruments if the path-dependent Asian payoff is hard to understand.")
elif audience == "Investor":
    st.subsection("Professional-investor checklist")
    st.markdown("- Stress the spot, volatility-of-volatility, correlation and jump assumptions.\n- Compare Heston and Bates outputs rather than relying on a point estimate.\n- Use delta/vega and model-risk reserves; reprice against the live option chain.")
else:
    st.subheader("Company checklist")
    st.markdown("- Align hedge notional with the company's actual cash-flow or commodity exposure.\n- Evaluate counterparty risk, basis risk, accounting treatment and liquidity.\n- Validate results in the treasury review framework and with qualified advisers.")

st.subheader("Rich / cheap relative to the calibrated model")
d = rich_cheap(ss.df, r["model"], S_DEMO, ss.T, R_DEMO, 0.0)
st.dataframe(d[["Strike", "Type", "Price", "Model", "Resid", "MktIV", "ModIV", "Signal"]], hide_index=True)

if AI_ON():
    ai_panel("Recommendations", {"audience": audience, "live_context": ss.get("home_live_context")}, [
        "Write a recommendation for this audience",
        "What would invalidate this recommendation?",
        "Create a scenario checklist for downside, normal and stressed markets",
    ])
