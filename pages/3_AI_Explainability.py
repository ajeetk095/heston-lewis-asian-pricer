import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('AI Explainability', '🔍')
st.title("Explainability"); ensure(); df = ss.df; r = ss.res; T = ss.T; p = ss.p
d = rich_cheap(df, r['model'], S_DEMO, T, R_DEMO, 0.0); t1,t2,t3,t4,t5 = st.tabs(["Residuals","Sensitivity","Integrand/CF","What-if & scenarios","IV surface"])
with t1:
    st.plotly_chart(px.bar(d, x=d.Strike.astype(str)+d.Type, y='Resid', title="Market − Model price"), width="stretch")
    st.plotly_chart(px.scatter(d, x='MktIV', y='ModIV', color='Type', title="Market vs model implied vol"), width="stretch")
    wide = d.pivot_table(index='Strike', columns='Type', values='Resid'); st.write("Residual correlation (calls vs puts):"); st.dataframe(wide.corr())
    st.plotly_chart(px.imshow(wide.T, aspect='auto', title="Residual heatmap (type × strike)", color_continuous_scale='RdBu_r', color_continuous_midpoint=0), width="stretch")
with t2:
    base = float(lewis_call(S_DEMO,S_DEMO,T,R_DEMO,0.0,p)[0]); rows=[]
    for i,nm in enumerate(PN):
        q = list(p); q[i] = q[i]*1.01 if q[i] else 0.001; rows.append((nm, (float(lewis_call(S_DEMO,S_DEMO,T,R_DEMO,0.0,tuple(q))[0])-base)/ (abs(p[i])*0.01 or 0.001)))
    sens = pd.DataFrame(rows, columns=["param","dPrice/dparam"]).assign(abs_rank=lambda x: x['dPrice/dparam'].abs()).sort_values('abs_rank', ascending=False)
    st.dataframe(sens); st.plotly_chart(px.bar(sens, x='param', y='dPrice/dparam', title="Parameter ranking (ATM call)"), width="stretch")
with t3:
    u, f = integrand(S_DEMO, S_DEMO, T, R_DEMO, 0.0, p); from utils.heston import heston_cf
    st.plotly_chart(go.Figure(go.Scatter(x=u[:800], y=f[:800])).update_layout(title="Lewis integrand (ATM)"), width="stretch")
    cf = heston_cf(u[:800], T, *p); st.plotly_chart(go.Figure([go.Scatter(x=u[:800], y=cf.real, name="Re φ"), go.Scatter(x=u[:800], y=cf.imag, name="Im φ")]).update_layout(title="Heston characteristic function"), width="stretch")
with t4:
    c = st.columns(3); sp = c[0].slider("Spot", 180., 290., S_DEMO); kk = c[1].slider("Strike", 180., 290., S_DEMO); dd = c[2].slider("Days", 5, 120, 20)
    st.metric("What-if call", f"${float(lewis_call(sp,kk,dd/250,R_DEMO,0.0,p)[0]):.3f}")
    grid = np.linspace(190,280,60); st.plotly_chart(px.line(x=grid, y=[float(lewis_call(s,kk,dd/250,R_DEMO,0.0,p)[0]) for s in grid], labels={'x':'Spot','y':'Call'}, title="Price vs spot"), width="stretch")
    reg = {"Calm":(.03,2,.03,.3,-.5),"Stressed":(.12,1,.1,.8,-.8),"Calibrated":p}; rows=[]
    for nm,pp in reg.items(): rows.append((nm, float(lewis_call(S_DEMO,S_DEMO,20/250,R_DEMO,0.0,pp)[0]), asian_call_qe(S_DEMO,S_DEMO,20/250,R_DEMO,0,pp,20,40000)[0]))
    st.write("Scenario regimes"); st.dataframe(pd.DataFrame(rows, columns=["Regime","Vanilla ATM 20d","Asian ATM 20d"]))
with t5:
    Ks = np.linspace(215, 250, 15); Ts = [10,20,40,60,90]; Z = np.array([[implied_vol(float(lewis_call(S_DEMO,k,t/250,R_DEMO,0.0,p)[0]),S_DEMO,k,t/250,R_DEMO,0.0,'C') for k in Ks] for t in Ts])
    st.plotly_chart(go.Figure(go.Surface(x=Ks, y=Ts, z=Z)).update_layout(title="Heston-implied vol surface (calibrated params)", scene=dict(xaxis_title='Strike', yaxis_title='Days', zaxis_title='IV')), width="stretch")
    st.caption("Market quotes exist only at the maturities in the dataset; the surface is the model's extrapolation.")

ai_button("🤖 Interpret the calibration diagnostics", "Interpret the calibration: fit quality, residual pattern, parameters on bounds, what the sensitivity ranking implies, and what to do next.", {"rmse": ss.get("res",{}).get("rmse"), "at_bounds": ss.get("res",{}).get("at_bounds")}, "AI Explainability")
ai_panel("AI Explainability", None, ["What does the residual heatmap tell me?", "Explain the Lewis integrand plot simply", "Compare calm vs stressed regimes"])
