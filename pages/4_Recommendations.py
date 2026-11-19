import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Recommendations', '💡')
st.title("Investment & Desk Recommendations"); ensure(); r = ss.res; p = ss.p
v = float(lewis_call(S_DEMO,S_DEMO,20/250,R_DEMO,0.0,p)[0]); a,se,ci = asian_call_qe(S_DEMO,S_DEMO,20/250,R_DEMO,0,p,20,100_000)
for line in recommendations(S_DEMO,S_DEMO,20/250,v,a,ci,r['rmse'],r['feller'],p): st.markdown("- "+line)
d = rich_cheap(ss.df, r['model'], S_DEMO, ss.T, R_DEMO, 0.0); st.subheader("Rich / cheap vs calibrated model"); st.dataframe(d[['Strike','Type','Price','Model','Resid','MktIV','ModIV','Signal']])
st.warning(DISC)

ai_button("🤖 Generate an investor brief", "Write a one-page investor brief: what the Asian call is, fair price vs client price, who it suits, three risks, three checks before trading. Use the app state; no guarantees.", None, "Recommendations")
ai_panel("Recommendations", None, ["Which options look rich or cheap and why?", "What hedges would a desk put on?", "What would change this recommendation?"])
