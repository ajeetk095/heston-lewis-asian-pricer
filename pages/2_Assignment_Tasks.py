import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Assignment Tasks', '📝')
R_ = get_results(); M = R_['meta']
st.title("GWP1 – Steps 1 to 3: answers, graphs and interpretation")
st.caption(f"Spot ${M['spot']}, risk-free {M['r']:.2%}, {M['days_per_year']} trading days per year, fee {M['fee']:.0%}. Numbers are computed by the same code as the notebook "
           f"(generated {M['generated'][:16].replace('T',' ')} UTC, {M['n_mc']:,} Monte Carlo paths).")

def fit_figs(fit, title):
    K, ty = np.array(fit['strike']), np.array(fit['type']); mk, md_ = np.array(fit['market']), np.array(fit['model_price'])
    f = go.Figure()
    for t_, c, nm in (('C', '#4C9BE8', 'calls'), ('P', '#E8574C', 'puts')):
        m = ty == t_
        f.add_trace(go.Scatter(x=K[m], y=mk[m], mode='markers', name=f'Market {nm}', marker=dict(color=c, size=9)))
        f.add_trace(go.Scatter(x=K[m], y=md_[m], mode='lines+markers', name=f'Model {nm}', line=dict(color=c, dash='dot'), marker=dict(symbol='x')))
    f.update_layout(title=title+" – price fit", xaxis_title="Strike ($)", yaxis_title="Option price ($)", height=360)
    g = go.Figure([go.Scatter(x=K, y=np.array(fit['mkt_iv'], float)*100, mode='markers', name='Market IV'), go.Scatter(x=K, y=np.array(fit['mod_iv'], float)*100, mode='markers', name='Model IV', marker=dict(symbol='x'))])
    g.update_layout(title="Implied volatility", xaxis_title="Strike ($)", yaxis_title="Implied volatility (%)", height=360)
    h = go.Figure(go.Bar(x=[f"{k:g}{t_}" for k, t_ in zip(K, ty)], y=np.array(fit['resid'])*-1, marker_color=np.where(ty == 'C', '#4C9BE8', '#E8574C')))
    h.update_layout(title="Pricing error (market − model)", xaxis_title="Strike and type", yaxis_title="$", height=360)
    c = st.columns(3); c[0].plotly_chart(f, width="stretch"); c[1].plotly_chart(g, width="stretch"); c[2].plotly_chart(h, width="stretch")

def params_table(fit):
    c = st.columns(4); c[0].metric("MSE", f"{fit['mse']:.5f}"); c[1].metric("RMSE ($)", f"{fit['rmse']:.3f}"); c[2].metric("Mean |IV error|", f"{fit['mean_abs_iv_err']:.2%}"); c[3].metric("Feller margin 2κθ−σ²", f"{fit['feller']:.3f}")
    st.dataframe(pd.DataFrame([fit['params']]).round(5), hide_index=True)
    if fit['at_bounds']: st.warning(f"Parameters on a bound: {', '.join(fit['at_bounds'])} → weakly identified; judge the fit by prices, not by individual parameters.")

d15, d60 = R_['data']['15'], R_['data']['60']
S1a, S1b, S1c, S2a, S2b, S2c, S3a, S3b = (R_[k] for k in ("step1a", "step1b", "step1c", "step2a", "step2b", "step2c", "step3a", "step3b"))
t = st.tabs(["Data check", "1a Heston–Lewis", "1b Heston–Carr-Madan", "1c Asian call", "2a Bates–Lewis", "2b Bates–Carr-Madan", "2c Put 70d", "3a CIR", "3b Euribor simulation"])

with t[0]:
    st.subheader("Are the quotes internally consistent? (put–call parity)")
    for lab, d in (("15 days", d15), ("60 days", d60)):
        st.markdown(f"**{lab}** – largest parity violation ${d['max_violation']:.2f}; irreducible MSE floor **{d['floor_mse']:.3f}**")
        st.dataframe(pd.DataFrame(d['table']).round(3), hide_index=True)
    st.info("Calls and puts in the supplied file do **not** satisfy put–call parity (gaps up to ≈$2–3, and the 60-day call prices even rise with strike at the low end). "
            "A model that is arbitrage-free cannot match both, so part of every calibration error is unavoidable. We compare each fit with the floor above.")

with t[1]:
    st.subheader("Q1a – Heston (1993), Lewis (2001), 15-day options, plain MSE")
    params_table(S1a); fit_figs(S1a, "Heston / Lewis, 15d")
    rob = R_['step1_robustness']; st.markdown("**Robustness – different optimiser seeds (same MSE, different parameters, same Asian price):**")
    st.dataframe(pd.DataFrame([{**{'seed': r['seed']}, **{k: round(v, 4) for k, v in r['params'].items()}, 'MSE': round(r['mse'], 5), 'Asian call 20d ($)': round(r['asian'], 3)} for r in rob]), hide_index=True)
    pf = R_['step1a_feller']
    st.markdown(f"**Interpretation.** RMSE ${S1a['rmse']:.3f}; the parity floor is {d15['floor_mse']:.3f}, i.e. {d15['floor_mse']/S1a['mse']:.0%} of the error is the data. "
                f"κ and θ are barely identified at a 15-day horizon (a Feller-penalised fit has MSE {pf['mse']:.4f} with κ={pf['params']['kappa']:.2f}, θ={pf['params']['theta']:.3f}). "
                f"What the data *do* pin down is v0, σ and ρ≈−1 (strong downside skew). Process: calibrated to all 10 quotes of the 15-day maturity (5 calls, 5 puts via put–call parity), objective = plain MSE, global differential evolution then L-BFGS-B, r = 1.5 %, T = 15/250.")

with t[1+1]:
    st.subheader("Q1b – Heston (1993), Carr–Madan (1999), 15-day options")
    params_table(S1b); fit_figs(S1b, "Heston / Carr-Madan, 15d")
    st.dataframe(pd.DataFrame({"Lewis": list(S1a['params'].values())+[S1a['mse']], "Carr-Madan": list(S1b['params'].values())+[S1b['mse']]}, index=list(S1a['params'])+["MSE"]).round(5))
    st.markdown(f"**Why similar (or not).** At identical parameters the two transforms differ by at most ${S1b['engine_gap_at_lewis_params']:.5f}: they are the same price function, so the fits are the same (MSE {S1a['mse']:.5f} vs {S1b['mse']:.5f}). "
                "Parameters can differ because the objective is almost flat in κ and θ; the well-identified ones (v0, σ, ρ) agree.")

with t[3]:
    st.subheader("Q1c – Asian call, ATM, 20 days, Monte Carlo, S₀ in the average, 4 % fee")
    q = S1c['qe']; c = st.columns(4); c[0].metric("Fair price", f"${q['price']:.4f}"); c[1].metric("95% CI", f"[{q['ci'][0]:.3f}, {q['ci'][1]:.3f}]"); c[2].metric("Fee (4%)", f"${q['fee']:.4f}"); c[3].metric("Client pays", f"${q['client']:.4f}")
    rows = [("QE, parameters of Q1a (headline)", S1c['qe']), ("Euler, same parameters", S1c['euler']), ("QE, Carr-Madan parameters", S1c['qe_cm_params']), ("QE, Feller-penalised parameters", S1c['qe_feller_params']), ("QE, S₀ wrongly excluded", S1c['qe_excl_s0'])]
    st.dataframe(pd.DataFrame([{'Variant': n_, 'Fair price': round(v['price'], 4), 'Std. error': round(v['se'], 4), 'Client price (+4%)': round(v['client'], 4)} for n_, v in rows]), hide_index=True)
    ec = S1c['european_check']; st.caption(f"Validation: Monte Carlo vanilla call ${ec['mc']:.4f} ± {ec['se']:.4f} vs closed form ${ec['fourier']:.4f} (z = {ec['z']:+.1f}). Vanilla ATM call: ${S1c['vanilla_lewis']:.2f}; the Asian is {1-q['price']/S1c['vanilla_lewis']:.0%} cheaper.")
    cv = np.array(S1c['convergence']); h = S1c['payoff_hist']; e = np.array(h['edges'])
    c = st.columns(2)
    c[0].plotly_chart(go.Figure(go.Scatter(x=cv[:, 0], y=cv[:, 1], error_y=dict(array=1.96*cv[:, 2]), mode='markers+lines')).update_layout(title="Monte Carlo convergence (95% interval)", xaxis_title="Simulated paths", yaxis_title="Asian call price ($)", xaxis_type="log", height=340), width="stretch")
    c[1].plotly_chart(go.Figure(go.Bar(x=(e[:-1]+e[1:])/2, y=h['counts'])).update_layout(title=f"Discounted payoff distribution ({h['prob_zero']:.0%} of paths pay zero)", xaxis_title="Payoff ($)", yaxis_title="Paths", height=340), width="stretch")
    st.markdown("**Plain-language summary for the client.** We looked at how the market currently prices ordinary SM options with about two weeks to expiry and found a set of assumptions about SM's price and its day-to-day swings that reproduces those prices closely. "
                "We then ran 200,000 possible daily price stories for the next 20 trading days, calculated for each the average price over the period (including today's price) and what your option would pay if that average ends above today's price. "
                f"The fair price (${q['price']:.2f}) is the average payoff discounted at 1.5 %. We add a 4 % fee (${q['fee']:.2f}), so you pay **${q['client']:.2f}**. Because the option depends on an *average*, it is cheaper than an ordinary option but pays out less in extreme moves. "
                "The result depends on assumptions we cannot observe directly, so the price is accurate to a few cents.")

with t[4]:
    st.subheader("Q2a – Bates (1996), Lewis (2001), 60-day options")
    params_table(S2a); fit_figs(S2a, "Bates / Lewis, 60d"); H = R_['heston60']
    st.markdown(f"**Interpretation.** Bates RMSE ${S2a['rmse']:.3f} vs Heston ${H['rmse']:.3f}; parity floor {d60['floor_mse']:.3f}. Jumps improve the fit by only {1-S2a['mse']/H['mse']:.1%}: {d60['floor_mse']/S2a['mse']:.0%} of the error comes from the inconsistent quotes. "
                f"ρ = {S2a['params']['rho']:+.2f} is atypical for equities and reflects parity violations that grow with strike, not a leverage effect. Eight parameters vs ten noisy quotes → do not interpret the jump block structurally.")
with t[5]:
    st.subheader("Q2b – Bates (1996), Carr–Madan (1999), 60-day options")
    params_table(S2b); fit_figs(S2b, "Bates / Carr-Madan, 60d")
    st.dataframe(pd.DataFrame({"Lewis": list(S2a['params'].values())+[S2a['mse']], "Carr-Madan": list(S2b['params'].values())+[S2b['mse']]}, index=list(S2a['params'])+["MSE"]).round(5))
    st.markdown(f"At identical parameters the transforms differ by ${S2b['engine_gap_at_lewis_params']:.5f}; equal MSE ⇒ same price function. Parameter differences reflect loose identification: compare prices, not parameters.")

with t[6]:
    st.subheader("Q2c – European put, 70 days, strike 95 % of spot")
    mdl = S2c['models']; hd = mdl[S2c['headline']]['mc']
    c = st.columns(4); c[0].metric("Strike", f"${S2c['K']:.2f}"); c[1].metric("Fair price (Bates MC)", f"${hd['price']:.3f}"); c[2].metric("Fee (4%)", f"${hd['fee']:.3f}"); c[3].metric("Client pays", f"${hd['client']:.3f}")
    names = {'bates_lewis': 'Bates, Lewis calibration (headline)', 'bates_cm': 'Bates, Carr-Madan calibration', 'bates_feller': 'Bates, Feller-penalised', 'heston60': 'Heston 60d', 'heston60_feller': 'Heston 60d, Feller-penalised',
             'heston60_put_quotes_only': 'Heston 60d, put quotes only', 'heston60_call_quotes_only': 'Heston 60d, call quotes only', 'heston15_not_appropriate': 'Heston 15d (too short-dated)'}
    st.dataframe(pd.DataFrame([{'Model / calibration': names[k], 'MC price': round(v['mc']['price'], 4), 'Std. error': round(v['mc']['se'], 4), 'Fourier price': round(v['fourier'], 4), 'z (MC vs Fourier)': round(v['z'], 1), 'Client price': round(v['mc']['client'], 3)} for k, v in mdl.items()]), hide_index=True)
    core = [mdl[k]['mc']['price'] for k in ('bates_lewis', 'bates_cm', 'bates_feller', 'heston60', 'heston60_feller')]
    h = S2c['payoff_hist']; e = np.array(h['edges'])
    st.plotly_chart(go.Figure(go.Bar(x=(e[:-1]+e[1:])/2, y=h['counts'])).update_layout(title=f"Discounted put payoff distribution ({h['prob_zero']:.0%} of paths expire worthless)", xaxis_title="Payoff ($)", yaxis_title="Paths", height=340), width="stretch")
    st.markdown(f"**Interpretation.** Fair premium **${hd['price']:.2f}** (95% CI ${hd['ci'][0]:.2f}–${hd['ci'][1]:.2f}); with the fee the client pays **${hd['client']:.2f}**; break-even at expiry ${S2c['breakeven']:.2f}. "
                f"Across the 60-day calibrations the put ranges ${min(core):.2f}–${max(core):.2f} (model-risk spread ${max(core)-min(core):.2f}); the put-only and call-only fits show how the call/put inconsistency moves the price. The 15-day parameters are not suitable for a 70-day option. Jumps are simulated in the Monte Carlo and the result is validated against the Fourier price.")
    st.markdown("**Plain-language summary for the client.** A put is insurance: you pay a premium now, and if SM's price on the expiry date (70 trading days away) is below 95 % of today's price you are compensated for the shortfall. We estimated the premium by simulating 200,000 possible futures, including occasional sudden jumps, and averaging the payouts. Most futures end above the protection level and pay nothing; a minority pay a lot. The premium plus our 4 % fee is the amount shown above.")

with t[7]:
    st.subheader("Q3a – CIR (1985) calibrated to the Euribor term structure")
    ts = S3a['term_structure']
    st.dataframe(pd.DataFrame({'Maturity': ts['labels'], 'Euribor, simple (%)': np.array(ts['simple'])*100, 'Discount factor': ts['discount'], 'Zero rate, continuous (%)': np.array(ts['zero'])*100}).round(4), hide_index=True)
    st.caption("Euribor quotes are simple rates: discount factor = 1/(1+L·τ); zero rate = ln(1+Lτ)/τ. A cubic spline through the zero rates gives 52 weekly points over 12 months, to which the CIR yield is fitted (r₀ = 1-week rate, Feller constraint 2κθ ≥ σ²).")
    c = st.columns(5); c[0].metric("κ", f"{S3a['kappa']:.3f}"); c[1].metric("θ", f"{S3a['theta']:.2%}"); c[2].metric("σ", f"{S3a['sigma']:.3f}"); c[3].metric("r₀", f"{S3a['r0']:.3%}"); c[4].metric("RMSE", f"{S3a['rmse_bp']:.1f} bp")
    tt = np.array(S3a['t'])*12; pr = np.array(S3a['profile'])
    f1 = go.Figure([go.Scatter(x=np.array(ts['tau'])*12, y=np.array(ts['zero'])*100, mode='markers', name='Euribor zero rates', marker=dict(size=10, color='red')), go.Scatter(x=tt, y=np.array(S3a['spline'])*100, name='Cubic spline', line=dict(dash='dash')), go.Scatter(x=tt, y=np.array(S3a['model'])*100, name='CIR')]).update_layout(title="CIR fit to the curve", xaxis_title="Maturity (months)", yaxis_title="Zero rate (%)", height=340)
    f2 = go.Figure(go.Bar(x=tt, y=(np.array(S3a['spline'])-np.array(S3a['model']))*1e4)).update_layout(title="Residuals (spline − CIR)", xaxis_title="Maturity (months)", yaxis_title="bp", height=340)
    f3 = go.Figure(go.Scatter(x=pr[:, 0], y=pr[:, 3], mode='lines+markers')).update_layout(title="σ is not identified by the curve", xaxis_title="Fixed σ", yaxis_title="Best-fit RMSE (bp)", height=340)
    c = st.columns(3); c[0].plotly_chart(f1, width="stretch"); c[1].plotly_chart(f2, width="stretch"); c[2].plotly_chart(f3, width="stretch")
    no = S3a['near_optimal']
    st.markdown(f"**Interpretation.** κ = {S3a['kappa']:.2f} (speed of mean reversion), θ = {S3a['theta']:.2%} (long-run level), σ = {S3a['sigma']:.2f}. RMSE {S3a['rmse_bp']:.1f} bp. κ and θ are driven by the steep slope of the curve and extrapolate far beyond 12 months. "
                f"σ is essentially **unidentified**: the fit is equally good for σ between {S3a['plateau'][0]:.2f} and {S3a['plateau'][1]:.2f}; we use the plateau midpoint and test sensitivity in 3b. "
                f"Alternatives: quoting the spline on simple rates gives RMSE {S3a['simple_convention']['rmse_bp']:.1f} bp; letting r₀ float gives {S3a['free_r0']['rmse_bp']:.1f} bp but misses the 1-week quote.")

with t[8]:
    st.subheader("Q3b – 100,000 daily paths of the 12-month Euribor over one year")
    cur, E = S3b['current'], S3b['expected']; cf = S3b['conf']
    c = st.columns(4); c[0].metric("Expected in 1y", f"{E:.2%}", f"{(E-cur)*1e4:+.0f} bp vs today"); c[1].metric("Today", f"{cur:.3%}"); c[2].metric("95% low (1y)", f"{cf['0.95'][0]:.2%}"); c[3].metric("95% high (1y)", f"{cf['0.95'][1]:.2%}")
    st.caption(f"99% range at one year: {cf['0.99'][0]:.2%} – {cf['0.99'][1]:.2%}; 90% range: {cf['0.90'][0]:.2%} – {cf['0.90'][1]:.2%}")
    days = np.array(S3b['days']); f = go.Figure()
    for j in range(np.array(S3b['samples']).shape[1]): f.add_trace(go.Scatter(x=days, y=np.array(S3b['samples'])[:, j]*100, mode='lines', line=dict(width=.5), opacity=.35, showlegend=False))
    f.add_trace(go.Scatter(x=days, y=np.array(S3b['hi95'])*100, line=dict(color='black', width=1), name='97.5th pct')); f.add_trace(go.Scatter(x=days, y=np.array(S3b['lo95'])*100, line=dict(color='black', width=1), fill='tonexty', fillcolor='rgba(0,0,0,.12)', name='2.5th pct'))
    f.add_trace(go.Scatter(x=days, y=np.array(S3b['mean_path'])*100, line=dict(color='red', width=3), name='Mean'))
    f.update_layout(title="Simulated 12M Euribor paths with 95% band", xaxis_title="Trading day", yaxis_title="12-month Euribor (%)", height=400)
    hh = S3b['hist']; ee = np.array(hh['edges'])
    g = go.Figure(go.Bar(x=(ee[:-1]+ee[1:])/2, y=hh['counts'])).update_layout(title="Distribution at the 1-year horizon", xaxis_title="12-month Euribor in one year (%)", yaxis_title="Paths", height=400)
    for x_ in cf['0.95']: g.add_vline(x=x_*100, line_dash="dot", line_color="purple")
    g.add_vline(x=E*100, line_color="red"); g.add_vline(x=cur*100, line_color="black", line_dash="dash")
    c = st.columns(2); c[0].plotly_chart(f, width="stretch"); c[1].plotly_chart(g, width="stretch")
    st.markdown(f"**(i) Range.** At 95 % confidence the 12M Euribor in one year lies between **{cf['0.95'][0]:.2%} and {cf['0.95'][1]:.2%}**. Over the whole year the 95 % band spans {S3b['envelope']['95'][0]:.2%}–{S3b['envelope']['95'][1]:.2%}; the absolute minimum / maximum over all 100,000 paths are {S3b['min_all']:.2%} / {S3b['max_all']:.2%}.")
    st.markdown(f"**(ii) Expected value.** **{E:.2%}** in one year vs {cur:.3%} today (+{(E-cur)*1e4:.0f} bp); {S3b['prob_above_current']:.1%} of paths end above today's level. It comes from the steep current curve extrapolated by the fitted model; equally good fits of the same curve give {no['ev_min']:.1%}–{no['ev_max']:.1%}.")
    sd = pd.DataFrame(S3b['sigma_sensitivity']); st.markdown("**Sensitivity to the unidentified σ** – the expected value barely moves, the width scales with σ:")
    st.dataframe(sd.rename(columns={'sigma': 'σ', 'mean': 'Expected', 'lo': '2.5%', 'hi': '97.5%'}).round(4), hide_index=True)
    imp = S3b['impact']; di = pd.DataFrame([{'Rate used': k, 'r': v['rate'], 'Asian call 20d ($)': round(v['asian20'], 4), 'Put 70d ($)': round(v['put70'], 4), '1y discount factor': round(v['discount_1y'], 4)} for k, v in imp.items()])
    st.markdown("**(iii) Effect on pricing.** Products re-priced at different rate levels (same random numbers):"); st.dataframe(di, hide_index=True)
    dA = imp['Expected 12M in 1y']['asian20']-imp['Today 12M Euribor']['asian20']; dP = imp['Expected 12M in 1y']['put70']-imp['Today 12M Euribor']['put70']
    st.markdown(f"Moving from today's 12M rate to the expected one changes the 20-day Asian call by **${dA:+.3f}** and the 70-day put by **${dP:+.3f}**; one-year discounting falls from {imp['Today 12M Euribor']['discount_1y']:.4f} to {imp['Expected 12M in 1y']['discount_1y']:.4f}. "
                "Higher rates raise call values and lower put values and discount factors. For these short-dated products the effect is small next to the volatility assumptions; for fixed-rate commitments and one-year funding it is material. "
                "The model is fitted to today's curve (risk-neutral), so these are scenarios, not statistical forecasts.")

ai_panel("Assignment Tasks", None, ["Summarise the key results of steps 1-3 for my boss", "Why do Lewis and Carr-Madan give nearly the same prices?", "What are the weaknesses of the Bates fit?"])
