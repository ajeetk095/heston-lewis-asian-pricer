import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Roadmap & Suggestions', '🧭')
st.markdown(hero("Roadmap & suggestions", "What to add to make the project stronger, and what to remove or merge so the app stays clean. Nothing here has been deleted – it is your call.",
                 ["Add", "Remove / simplify"]), unsafe_allow_html=True)
LV = {"High": "high", "Medium": "med", "Low": "low"}
ADD = [
 ("Deploy the app live", "High", "Low", "Push the repo to GitHub and deploy on Streamlit Community Cloud (steps in deployment.md). The brief asks for a live app; a public link is the single most valuable addition."),
 ("Recalibrate on cleaned data", "High", "Low", "Calibrate only to out-of-the-money options (calls above spot, puts below) so the put–call parity violations stop polluting the fit. Report the lower MSE next to the raw one."),
 ("Parameter uncertainty bands", "High", "Medium", "Re-run the calibration from many seeds / bootstrap the quotes and show the spread of κ, θ, σ, ρ. This turns the 'parameters are weakly identified' caveat into evidence."),
 ("σ and confidence what-if for Step 3b", "Medium", "Low", "Let the reader change the CIR volatility and the confidence level and watch the Euribor range and the put price move."),
 ("Download results (CSV / Excel)", "Medium", "Low", "One button on the Report page exporting prices, parameters and scenario percentiles, so figures can be checked outside the app."),
 ("Control variate for the Asian call", "Medium", "Medium", "Use the geometric Asian option (closed form) as a control variate to shrink Monte Carlo error with fewer paths."),
 ("Asian-option Greeks", "Medium", "Medium", "Delta and vega of the Asian call by pathwise or bump-and-reprice, shown next to the price."),
 ("Heston with stochastic rates", "Medium", "High", "Drive the discount rate with the calibrated CIR paths inside the Asian/put Monte Carlo. Natural extension of Step 3, but a research task of its own."),
 ("Continuous integration", "Low", "Low", "A GitHub Actions workflow running the 43 tests on every push, so the live app never breaks silently."),
]
REMOVE = [
 ("AI Assistant and 'Ask AI' panels", "They need a paid/third-party key and are not part of the brief. Already hidden automatically when OPENROUTER_API_KEY is absent; delete the files if you never plan to use them.", "Optional"),
 ("Presentation page", "Duplicates the slide deck that can be downloaded from the Research Report page. Merge it there and drop the separate page.", "Merge"),
 ("About Developer + Contact + Disclaimer + Documentation", "Four near-empty pages. Combine them into one 'About' page; the sidebar becomes much shorter.", "Merge"),
 ("Recommendations (rich/cheap) page", "Not requested in the brief and reads like investment advice, which the disclaimer says it is not. Remove it or label it clearly as illustrative.", "Optional"),
 ("Real-Time Data page", "Depends on external web services and can fail on a hosted server. Keep only if you want a live-market demo; it is not graded.", "Optional"),
 ("Learn page", "Overlaps with the explanations already in the notebook and the Assignment Tasks tabs.", "Merge"),
 ("Live Simulation vs Model Diagnostics", "Both explore the same calibrated model. Keep one 'Explore' page with tabs if you want fewer entries.", "Merge"),
]
t1, t2, t3 = st.tabs(["➕ What to add", "➖ What to remove", "🧭 Suggested order"])
with t1:
    f = st.segmented_control("Filter by impact", ["All", "High", "Medium", "Low"], default="All")
    items = [a for a in ADD if f in (None, "All") or a[1] == f]
    for i in range(0, len(items), 2):
        cols = st.columns(2)
        for col, (t, imp, eff, d) in zip(cols, items[i:i+2]):
            col.markdown(card(t, d, tags=tag(LV[imp], f"Impact: {imp}") + tag("low", f"Effort: {eff}")), unsafe_allow_html=True)
        st.write("")
with t2:
    st.caption("None of these is an error. They are ways to make the app shorter and more focused on the graded work.")
    for i in range(0, len(REMOVE), 2):
        cols = st.columns(2)
        for col, (t, d, k) in zip(cols, REMOVE[i:i+2]):
            col.markdown(card(t, d, tags=tag("rm", k)), unsafe_allow_html=True)
        st.write("")
with t3:
    st.markdown("""
1. **Before submission:** deploy live, confirm the front pages of the PDF are your group's template, and check that the numbers on *Home* match the report.
2. **If time allows:** recalibrate on cleaned data and add parameter uncertainty bands – these directly address the biggest weakness (data quality).
3. **Polish:** merge the small info pages, hide anything you will not demo.
4. **Later:** Asian Greeks, control variate, stochastic-rate Heston.
""")
