import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Live Simulation', '📈')
st.title("Live Simulation"); ensure(); d = ss.p
up = st.file_uploader("Optional CSV (Days to maturity, Strike, Price, Type) to calibrate on – max 200 rows", type="csv")
if up:
    try:
        if up.size > 1_000_000: raise ValueError("file larger than 1 MB")
        u, err = validate_upload(pd.read_csv(up, nrows=MAX_UPLOAD_ROWS + 1))
        if err: st.error(err)
        else:
            dd = st.selectbox("Maturity (days) to calibrate", sorted(u['Days to maturity'].unique()))
            if st.button("Calibrate on upload"):
                uu = u[u['Days to maturity'] == dd].reset_index(drop=True)
                if len(uu) < 4: st.error("Need at least 4 quotes at the chosen maturity.")
                else:
                    with heavy("calibration"), st.spinner("Calibrating…"): res = calibrate(uu, S_DEMO, R_DEMO, 0.0, dd/250, maxiter=60)
                    ss.p = tuple(res['params']); ss.res = res; ss.df = uu; ss.T = dd/250; d = ss.p
    except Exception: st.error("Could not read that file. Please upload a plain CSV with the four required columns.")
c = st.columns(5); lim = [(1e-3, 1.0), (1e-2, 8.0), (1e-3, 1.0), (1e-2, 2.0), (-.99, .99)]
p = tuple(c[i].number_input(n, min_value=lim[i][0], max_value=lim[i][1], value=float(np.clip(d[i], *lim[i])), format="%.4f", key="p"+n) for i, n in enumerate(PN))
c = st.columns(5); S = c[0].number_input("Spot", 1.0, 5000.0, S_DEMO); K = c[1].number_input("Strike", 1.0, 5000.0, S_DEMO); days = c[2].number_input("Days", 1, 750, 20)
r = c[3].number_input("Rate", -0.05, 0.25, R_DEMO, format="%.4f"); q = c[4].number_input("Div yield", 0.0, 0.25, 0.0, format="%.4f"); T = days/250
typ = st.radio("Vanilla type", ["C","P"], horizontal=True); n = st.slider("MC paths (capped automatically for long maturities)", 20_000, 200_000, 100_000, 20_000)
sch = st.radio("MC scheme", ["QE (Andersen)", "Euler full-truncation"], horizontal=True)
v = float(model_price(S, K, T, r, q, p, typ)[0]); iv = implied_vol(v, S, K, T, r, q, typ)
n = mc_paths(n, days)
with heavy("simulation"): a, se, ci = (asian_call_qe if sch.startswith("QE") else asian_call_mc)(S, K, T, r, q, p, int(days), n)  # S0 is in the average
m = st.columns(4); m[0].metric("Vanilla (Lewis)", f"${v:.4f}"); m[1].metric("Implied vol", f"{iv:.2%}"); m[2].metric("Asian call (MC)", f"${a:.4f}"); m[3].metric("95% CI", f"[{ci[0]:.3f}, {ci[1]:.3f}]")
st.info(f"Client price with 4% fee: ${a*1.04:.4f}")
g = greeks(S, K, T, r, q, p, typ); st.dataframe(pd.DataFrame([g]))
ss.last = dict(p=p, vanilla=v, asian=a, K=K, days=days); ss.asian = (a, se, ci)
st.write(f"With v0={p[0]:.3f}, κ={p[1]:.2f}, θ={p[2]:.3f}, σ={p[3]:.2f}, ρ={p[4]:.2f}, the Lewis formula prices the {days}-day {K:.0f}-strike {'call' if typ=='C' else 'put'} at ${v:.2f}. The Asian call over daily monitoring is ${a:.2f} (95% CI ±{1.96*se:.3f}).")
from utils.asian_mc import simulate
_, pay = simulate(S, K, T, r, q, p, int(days), mc_paths(min(n, 100_000), days), 42, "heston", "asian_call", "qe", return_payoffs=True)
st.plotly_chart(px.histogram(x=pay[pay > 0], nbins=60, title=f"Simulated discounted Asian payoffs ({(pay == 0).mean():.0%} of paths pay zero)", labels={'x': 'Payoff ($)', 'count': 'Paths'}), width="stretch")
st.success("**Insight:** Asian value < vanilla because averaging dampens volatility. Prefer QE when Feller is violated.")

ai_button("🤖 Explain this pricing result", "Explain these pricing results in plain language for (a) a trader and (b) an investor: Asian vs vanilla gap, Monte Carlo error, main risks.", {"last": ss.get("last")}, "Live Simulation")
ai_panel("Live Simulation", {"last": ss.get("last")}, ["Why is the Asian cheaper than the vanilla?", "Which Heston parameter matters most here?", "How could I improve this calibration?"])
