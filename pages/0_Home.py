import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Home', '🏠')
R_ = get_results(); ensure()
s1, s2, s3 = R_['step1c'], R_['step2c'], R_['step3b']; put = s2['models'][s2['headline']]['mc']
st.markdown(hero("SM Energy: Heston, Bates, Asian & put pricing with CIR rate scenarios",
    "MScFE 622 Group Work Project 1 – calibration (Lewis 2001, Carr–Madan 1999), Monte Carlo pricing and Euribor scenarios, with notebook and report.",
    ["Heston", "Bates jumps", "Lewis & Carr–Madan", "Asian MC", "CIR / Euribor"]), unsafe_allow_html=True)
k = st.columns(4)
for col, (l, v, sub) in zip(k, [
    ("Asian call 20d ATM – fair", f"${s1['qe']['price']:.2f}", "Monte Carlo, S0 in average"),
    ("Asian call – client pays", f"${s1['qe']['client']:.2f}", "fair price + 4% fee"),
    (f"Put 70d K=${s2['K']:.2f} – client", f"${put['client']:.2f}", f"fair ${put['price']:.2f}"),
    ("12M Euribor in 1y", f"{s3['expected']:.2%}", f"{(s3['expected']-s3['current'])*1e4:+.0f} bp vs today")]):
    col.markdown(kpi(l, v, sub), unsafe_allow_html=True)
st.write("")
c1, c2 = st.columns([3, 2])
with c1:
    fig = go.Figure()
    fig.add_bar(name="Fair price", x=["Asian call 20d", "Put 70d"], y=[s1['qe']['price'], put['price']])
    fig.add_bar(name="Client pays (+4%)", x=["Asian call 20d", "Put 70d"], y=[s1['qe']['client'], put['client']])
    fig.update_layout(barmode="group", title="Fair price vs client price ($)", height=330)
    st.plotly_chart(fig, width="stretch")
with c2:
    lo, hi = s3['conf']['0.95']
    f2 = go.Figure(go.Indicator(mode="number+gauge", value=s3['expected']*100, number=dict(suffix="%", valueformat=".2f"),
        gauge=dict(shape="bullet", axis=dict(range=[0, max(10, hi*100+1)]), bar=dict(color=ACCENT),
                   steps=[dict(range=[lo*100, hi*100], color="rgba(124,140,255,.35)")]),
        title=dict(text="12M Euribor in 1 year<br><span style='font-size:.75em'>bar = expected, band = 95% range</span>")))
    f2.update_layout(height=330); st.plotly_chart(f2, width="stretch")
st.caption(f"95% range: {lo:.2%} – {hi:.2%}. Spot $232.90, r = 1.50%, 250 trading days/year.")
st.warning("Data caveat: the supplied calls and puts violate put–call parity (up to ≈$3 at 60 days), so every calibration carries an irreducible error and individual Heston/Bates parameters are weakly identified. Prices are robust; parameters are not.")
st.subheader("Where each requirement of the brief is answered")
steps = [("Step 1a – Heston + Lewis", "15 days: parameters, process, fit graphs.", "Assignment Tasks → 1a"),
         ("Step 1b – Heston + Carr–Madan", "Why the parameters are (not) similar.", "Assignment Tasks → 1b"),
         ("Step 1c – Asian call", "ATM 20d, Monte Carlo, 4% fee, plain-language note.", "Assignment Tasks → 1c"),
         ("Step 2 – Bates & put", "60d Bates with both methods; 70d put at 95%.", "Assignment Tasks → 2a–2c"),
         ("Step 3 – CIR & Euribor", "Cubic-spline weekly curve, 100,000 paths, pricing impact.", "Assignment Tasks → 3a, 3b"),
         ("Step 4 – Deliverables", "Notebook + HTML zip and answers-only PDF.", "Research Report page")]
for row in (steps[:3], steps[3:]):
    cols = st.columns(3)
    for col, (t, d, w) in zip(cols, row):
        col.markdown(card(t, f"{d}  →  {w}", n=steps.index((t, d, w)) + 1), unsafe_allow_html=True)
    st.write("")
c = st.columns(4)
for col, (pth, lab, ic) in zip(c, [("pages/2_Assignment_Tasks.py", "Assignment answers", "📝"), ("pages/8_Research_Report.py", "Report & downloads", "📄"),
                                   ("pages/1_Live_Simulation.py", "Live pricing sandbox", "📈"), ("pages/14_Roadmap.py", "Roadmap & suggestions", "🧭")]):
    with col: plink(pth, lab, ic)
ai_panel("Home", None, ["What does this app do?", "Give me the headline result in two sentences", "Where should an investor start?"])
