"""Build reports/GWP1_report.pdf: answers only (no code), technical + non-technical, MLA references.
Pages 1-2 (cover + member/integrity form) come from the group's original submission."""
import sys, tempfile, io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from pypdf import PdfReader, PdfWriter
from utils import pipeline
from utils.paths import REPORT_DIR

R = pipeline.load(); TMP = Path(tempfile.mkdtemp())
ss = getSampleStyleSheet()
BODY = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10, leading=14, spaceAfter=6)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=16, spaceBefore=10, spaceAfter=8)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12.5, spaceBefore=10, spaceAfter=5)
H3 = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=10.5, spaceBefore=6, spaceAfter=3)
CAP = ParagraphStyle("c", parent=BODY, fontSize=8.5, leading=11, textColor=colors.HexColor("#444444"), spaceAfter=10)
P = lambda t, s=BODY: Paragraph(t, s)
story = []; fig_n = [0]; tab_n = [0]


def fig(fn, caption, w=16.5):
    fig_n[0] += 1; path = TMP / f"f{fig_n[0]}.png"; fn(); plt.savefig(path, dpi=170, bbox_inches="tight"); plt.close("all")
    from PIL import Image as PI
    w_, h_ = PI.open(path).size
    story.append(KeepTogether([Image(str(path), width=w * cm, height=w * cm * h_ / w_), P(f"<b>Figure {fig_n[0]}.</b> {caption}", CAP)]))


def table(rows, header, caption, widths=None):
    tab_n[0] += 1
    t = Table([header] + rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                           ("GRID", (0, 0), (-1, -1), .4, colors.grey), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]), ("ALIGN", (1, 0), (-1, -1), "RIGHT")]))
    story.append(KeepTogether([P(f"<b>Table {tab_n[0]}.</b> {caption}", CAP), t, Spacer(1, 8)]))


def fit_plot(fit, title):
    def f():
        K, ty = np.array(fit["strike"]), np.array(fit["type"]); mk, md = np.array(fit["market"]), np.array(fit["model_price"])
        fg, a = plt.subplots(1, 3, figsize=(15, 4.2))
        for t_, c in (("C", "tab:blue"), ("P", "tab:red")):
            m = ty == t_; a[0].plot(K[m], mk[m], "o", c=c, label="Market " + ("calls" if t_ == "C" else "puts")); a[0].plot(K[m], md[m], "-x", c=c, label="Model")
        a[0].set(xlabel="Strike ($)", ylabel="Option price ($)", title="Price fit"); a[0].legend(fontsize=8)
        a[1].plot(K, np.array(fit["mkt_iv"], float) * 100, "bo", label="Market"); a[1].plot(K, np.array(fit["mod_iv"], float) * 100, "rx", label="Model"); a[1].set(xlabel="Strike ($)", ylabel="Implied volatility (%)", title="Implied volatility"); a[1].legend(fontsize=8)
        a[2].bar([f"{k:g}{t}" for k, t in zip(K, ty)], -np.array(fit["resid"])); a[2].set(xlabel="Strike and type", ylabel="Market minus model ($)", title="Pricing error"); a[2].tick_params(axis="x", rotation=60)
        for x in a: x.grid(alpha=.3)
        fg.suptitle(title); plt.tight_layout()
    return f


def ptable(fit, extra=None):
    nm = list(fit["params"]); vals = [f"{fit['params'][k]:.4f}" for k in nm]
    table([vals + [f"{fit['mse']:.5f}", f"{fit['rmse']:.3f}", f"{fit['feller']:.3f}"]], nm + ["MSE", "RMSE ($)", "Feller margin"], extra or "Calibrated parameters and fit quality.")


M, d15, d60 = R["meta"], R["data"]["15"], R["data"]["60"]
S1a, S1b, S1c, S2a, S2b, S2c, S3a, S3b, H60 = (R[k] for k in ("step1a", "step1b", "step1c", "step2a", "step2b", "step2c", "step3a", "step3b", "heston60"))
hd = S2c["models"][S2c["headline"]]; q = S1c["qe"]; put = hd["mc"]; pct = lambda x: f"{x:.2%}"

# ---------------- body
story += [P("Introduction", H1),
          P("This report answers Group Work Project 1 of MScFE 622 (Stochastic Modeling) for SM Energy. Spot is $232.90, the risk-free rate is 1.50%, a year has 250 trading days and no dividends are paid. "
            "Step 1 calibrates the Heston model with the Lewis and Carr-Madan Fourier formulas and prices a 20-day at-the-money Asian call; Step 2 repeats the exercise with the Bates jump model at 60 days and prices a 70-day put; "
            "Step 3 calibrates the Cox-Ingersoll-Ross model to the Euribor curve and simulates the 12-month rate. Every question has a technical answer and a plain-language answer. "
            "The executable notebook accompanies this report; no code appears here."),
          P("Data check: the option quotes are not internally consistent", H2),
          P(f"The supplied calls and puts violate put-call parity: the largest gap between the call-minus-put price and its no-arbitrage value is ${d15['max_violation']:.2f} at 15 days and ${d60['max_violation']:.2f} at 60 days, and the 60-day call prices rise with strike at the low end. "
            f"No arbitrage-free model can match both sides, so every calibration has an unavoidable error. The smallest mean squared error achievable is {d15['floor_mse']:.3f} at 15 days and {d60['floor_mse']:.3f} at 60 days (the sum of squared parity gaps divided by four times the number of strikes). "
            "We compare each fit with this floor and judge the models by prices rather than by single parameter values."),
          P("Step 1", H1), P("Question 1a: Heston model, Lewis (2001) formula, 15-day options", H2), P("Technical answer", H3),
          P("Process. The Heston (1993) model has five parameters: initial variance v0, mean-reversion speed kappa, long-run variance theta, volatility of variance sigma and correlation rho. "
            "Call prices come from the Lewis (2001) single-integral formula with the Heston characteristic function; put prices follow from put-call parity. "
            "The loss is the plain mean squared error over all ten 15-day quotes (five calls, five puts). It is minimised by a global differential-evolution search followed by a bounded local polish. Maturity is 15/250 years.")]
ptable(S1a, "Heston parameters, Lewis formula, 15 days (regular MSE).")
fig(fit_plot(S1a, "Heston calibrated with the Lewis formula, 15 days"), "Market and model prices, implied volatilities and pricing errors.")
rob = R["step1_robustness"]; pf = R["step1a_feller"]
table([[str(r_["seed"])] + [f"{r_['params'][k]:.3f}" for k in r_["params"]] + [f"{r_['mse']:.5f}", f"{r_['asian']:.3f}"] for r_ in rob], ["Seed"] + list(rob[0]["params"]) + ["MSE", "Asian call ($)"],
      "Robustness: different optimiser seeds give different parameters, the same MSE and the same Asian price.")
story += [P(f"The fit has a root mean squared error of ${S1a['rmse']:.3f} (mean squared error {S1a['mse']:.4f}); the parity floor is {d15['floor_mse']:.4f}, so about {d15['floor_mse']/S1a['mse']:.0%} of the error is a property of the data. "
            f"The mean absolute implied-volatility error is {S1a['mean_abs_iv_err']:.2%}. Correlation is at its lower limit of -0.99 and the mean-reversion parameters sit on or near their bounds ({', '.join(S1a['at_bounds']) or 'none'}): over only 15 days the data cannot identify long-run behaviour. "
            f"Adding a Feller penalty (not required by the brief) moves kappa to {pf['params']['kappa']:.2f} and theta to {pf['params']['theta']:.3f} but changes the MSE only from {S1a['mse']:.4f} to {pf['mse']:.4f}. "
            "The data pin down the initial variance, the volatility of variance and the strongly negative correlation (a pronounced downside skew); we therefore rely on prices rather than on kappa and theta."),
          P("Non-technical answer", H3),
          P("We looked for the settings of a well-known model of stock-price behaviour that best reproduce the option prices quoted today for the next 15 days. The model matches the quotes to within about 50 cents on average, and most of that gap comes from the quotes disagreeing with each other. "
            "Several different settings fit equally well, so we trust the resulting prices more than any single setting."),
          P("Question 1b: Heston model, Carr-Madan (1999) formula, 15-day options", H2), P("Technical answer", H3)]
ptable(S1b, "Heston parameters, Carr-Madan formula, 15 days.")
fig(fit_plot(S1b, "Heston calibrated with the Carr-Madan formula, 15 days"), "Market and model prices, implied volatilities and pricing errors.")
story += [P(f"The same data, loss and optimiser are used; only the pricing transform changes (damping factor 1.5). At identical parameters the two formulas differ by at most ${S1b['engine_gap_at_lewis_params']:.5f}, because both are exact representations of the same Heston price. "
            f"Hence the fits coincide (MSE {S1a['mse']:.5f} for Lewis and {S1b['mse']:.5f} for Carr-Madan). The parameters need not coincide: kappa is {S1a['params']['kappa']:.3f} versus {S1b['params']['kappa']:.3f} and theta {S1a['params']['theta']:.4f} versus {S1b['params']['theta']:.4f}, "
            f"because the objective is almost flat in these two directions and each run stops at a different point of the same flat valley. The well-identified parameters agree: v0 {S1a['params']['v0']:.3f} versus {S1b['params']['v0']:.3f}, sigma {S1a['params']['sigma']:.2f} versus {S1b['params']['sigma']:.2f} and rho {S1a['params']['rho']:.2f} versus {S1b['params']['rho']:.2f}. "
            "Similar prices, not identical parameters, is the correct outcome."),
          P("Non-technical answer", H3), P("Two different mathematical shortcuts for computing option prices give the same prices, so they find equally good settings. The settings that matter for 15-day prices are nearly identical; the others are loosely determined and can differ without changing any price."),
          P("Question 1c: Asian call, at the money, 20 days, with 4% fee", H2), P("Technical answer", H3),
          P(f"Process. We simulate 200,000 risk-neutral paths (100,000 antithetic pairs) with 20 daily steps using the parameters of question 1a, the Andersen quadratic-exponential variance scheme with a martingale correction, and the risk-free rate as drift. "
            "The payoff is the larger of (average of the 21 prices from today to expiry, with today's price included) minus the strike (equal to spot), and zero; it is discounted at 1.50%.")]
table([["Quadratic-exponential, parameters of 1a (headline)", f"{q['price']:.4f}", f"{q['se']:.4f}", f"{q['client']:.4f}"], ["Euler scheme, same parameters", f"{S1c['euler']['price']:.4f}", f"{S1c['euler']['se']:.4f}", f"{S1c['euler']['client']:.4f}"],
       ["Parameters of 1b (Carr-Madan)", f"{S1c['qe_cm_params']['price']:.4f}", f"{S1c['qe_cm_params']['se']:.4f}", f"{S1c['qe_cm_params']['client']:.4f}"], ["Feller-penalised parameters", f"{S1c['qe_feller_params']['price']:.4f}", f"{S1c['qe_feller_params']['se']:.4f}", f"{S1c['qe_feller_params']['client']:.4f}"],
       ["Today's price wrongly left out of the average", f"{S1c['qe_excl_s0']['price']:.4f}", f"{S1c['qe_excl_s0']['se']:.4f}", f"{S1c['qe_excl_s0']['client']:.4f}"]],
      ["Variant", "Fair price ($)", "Std. error ($)", "Client price, +4% ($)"], "Asian call price under alternative settings.", [8 * cm, 3 * cm, 3 * cm, 3.5 * cm])


def conv_f():
    cv = np.array(S1c["convergence"]); h = S1c["payoff_hist"]; e = np.array(h["edges"]); fg, a = plt.subplots(1, 2, figsize=(13, 4))
    a[0].errorbar(cv[:, 0], cv[:, 1], yerr=1.96 * cv[:, 2], fmt="o-", capsize=3); a[0].set(xscale="log", xlabel="Simulated paths", ylabel="Asian call price ($)", title="Convergence (95% interval)")
    a[1].bar((e[:-1] + e[1:]) / 2, h["counts"], width=e[1] - e[0]); a[1].set(xlabel="Discounted payoff ($)", ylabel="Number of paths", title=f"Payoff distribution ({h['prob_zero']:.0%} pay zero)")
    for x in a: x.grid(alpha=.3)
    plt.tight_layout()


fig(conv_f, "Monte Carlo convergence and the distribution of discounted payoffs.", 14)
ec = S1c["european_check"]
story += [P(f"The fair price is <b>${q['price']:.2f}</b> (standard error ${q['se']:.3f}; 95% interval ${q['ci'][0]:.2f} to ${q['ci'][1]:.2f}). The 4% fee adds ${q['fee']:.2f}, so the client pays <b>${q['client']:.2f}</b>. "
            f"The same simulation reproduces the closed-form price of a vanilla at-the-money call (${ec['fourier']:.3f} analytic, ${ec['mc']:.3f} simulated, {ec['z']:+.1f} standard errors), which validates the scheme; the Euler scheme is less reliable. "
            f"The Asian option is {1-q['price']/S1c['vanilla_lewis']:.0%} cheaper than the vanilla (${S1c['vanilla_lewis']:.2f}) because averaging reduces volatility. Other calibrations change the price by at most ${max(abs(S1c[k]['price']-q['price']) for k in ('euler','qe_cm_params','qe_feller_params')):.2f}: the price is robust even though the parameters are not."),
          P("Non-technical answer", H3),
          P(f"We ran 200,000 possible daily price stories for the next 20 trading days. For each, we averaged the price over the period (including today's) and checked whether it ended above today's price; the option pays the difference. "
            f"The fair price (${q['price']:.2f}) is the average payout, discounted. We add a 4% fee (${q['fee']:.2f}), so you pay ${q['client']:.2f}. The option is cheaper than an ordinary one because an average moves less than a single day's price. The price is accurate to a few cents."),
          PageBreak(), P("Step 2", H1), P("Question 2a: Bates model, Lewis formula, 60-day options", H2), P("Technical answer", H3),
          P("Process. The Bates (1996) model adds log-normal jumps to Heston: jump intensity lambda, mean log-jump and jump volatility. The eight parameters are calibrated to the ten 60-day quotes with the same Lewis pricing, put-call parity and plain MSE loss.")]
ptable(S2a, "Bates parameters, Lewis formula, 60 days.")
fig(fit_plot(S2a, "Bates calibrated with the Lewis formula, 60 days"), "Market and model prices, implied volatilities and pricing errors.")
story += [P(f"The Bates fit has RMSE ${S2a['rmse']:.3f} (MSE {S2a['mse']:.3f}) against ${H60['rmse']:.3f} (MSE {H60['mse']:.3f}) for Heston at the same maturity, and the parity floor is {d60['floor_mse']:.3f}. "
            f"Jumps therefore improve the fit by only {1-S2a['mse']/H60['mse']:.1%}: about {d60['floor_mse']/S2a['mse']:.0%} of the remaining error comes from the inconsistent quotes. "
            f"The estimated correlation is {S2a['params']['rho']:+.2f}. A positive value is unusual for an equity and reflects call and put prices that disagree increasingly with strike, not a leverage effect. Parameters on a bound: {', '.join(S2a['at_bounds']) or 'none'}. "
            "Eight parameters against ten noisy quotes means the jump parameters are weakly identified and should not be read structurally."),
          P("Non-technical answer", H3), P("We added occasional sudden price jumps to the model, which helps a little. But most of the remaining mismatch is because the call and put prices we were given contradict each other, which no model can fix."),
          P("Question 2b: Bates model, Carr-Madan formula, 60-day options", H2), P("Technical answer", H3)]
ptable(S2b, "Bates parameters, Carr-Madan formula, 60 days.")
fig(fit_plot(S2b, "Bates calibrated with the Carr-Madan formula, 60 days"), "Market and model prices, implied volatilities and pricing errors.")
story += [P(f"The MSE is {S2a['mse']:.5f} with Lewis and {S2b['mse']:.5f} with Carr-Madan. At identical parameters the two formulas differ by at most ${S2b['engine_gap_at_lewis_params']:.5f}, so they are the same price function and the fits agree. "
            f"The largest parameter difference between the two runs is {max(abs(S2a['params'][k]-S2b['params'][k]) for k in S2a['params']):.2f}; eight loosely identified parameters can trade off against each other without changing prices, so prices and MSE are the meaningful comparison."),
          P("Non-technical answer", H3), P("Using the second pricing shortcut gives the same fit quality and the same prices; only the settings that do not affect prices differ."),
          P("Question 2c: European put, 70 days, strike at 95% of spot", H2), P("Technical answer", H3),
          P(f"Process. The put (strike ${S2c['K']:.2f}) is priced by Monte Carlo under the Bates dynamics calibrated in 2a, with 70 daily steps, simulated jumps, 200,000 paths and the same variance scheme, then cross-checked against the Fourier price. "
            "The 60-day calibration is the closest available maturity (quotes exist at 15, 60 and 120 days); the 15-day parameters are too short-dated and are shown only for contrast.")]
nm = {"bates_lewis": "Bates, Lewis calibration (headline)", "bates_cm": "Bates, Carr-Madan calibration", "bates_feller": "Bates, Feller-penalised", "heston60": "Heston 60 days", "heston60_feller": "Heston 60 days, Feller-penalised",
      "heston60_put_quotes_only": "Heston 60 days, put quotes only", "heston60_call_quotes_only": "Heston 60 days, call quotes only", "heston15_not_appropriate": "Heston 15 days (too short-dated)"}
table([[nm[k], f"{v['mc']['price']:.3f}", f"{v['mc']['se']:.3f}", f"{v['fourier']:.3f}", f"{v['mc']['client']:.3f}"] for k, v in S2c["models"].items()],
      ["Model and calibration", "Monte Carlo ($)", "Std. error", "Fourier ($)", "Client, +4% ($)"], "Put price under alternative models and calibrations.", [7 * cm, 2.5 * cm, 2.2 * cm, 2.5 * cm, 3 * cm])
core = [S2c["models"][k]["mc"]["price"] for k in ("bates_lewis", "bates_cm", "bates_feller", "heston60", "heston60_feller")]


def put_f():
    h = S2c["payoff_hist"]; e = np.array(h["edges"]); plt.figure(figsize=(8, 3.8)); plt.bar((e[:-1] + e[1:]) / 2, h["counts"], width=e[1] - e[0], color="tab:red")
    plt.xlabel("Discounted put payoff ($)"); plt.ylabel("Number of paths"); plt.title(f"Put payoff distribution ({h['prob_zero']:.0%} expire worthless)"); plt.grid(alpha=.3)


fig(put_f, "Distribution of discounted put payoffs under the Bates model.", 11)
story += [P(f"The fair price is <b>${put['price']:.2f}</b> (95% interval ${put['ci'][0]:.2f} to ${put['ci'][1]:.2f}); with the 4% fee (${put['fee']:.2f}) the client pays <b>${put['client']:.2f}</b>, and the break-even stock price at expiry is ${S2c['breakeven']:.2f}. "
            f"The simulation agrees with the Fourier price ({hd['z']:+.1f} standard errors). Across the 60-day calibrations the put ranges from ${min(core):.2f} to ${max(core):.2f}, a model-risk spread of ${max(core)-min(core):.2f} that a trading desk should cover with a reserve; "
            "calibrating to puts only or calls only shows how much the inconsistency between the two moves the answer."),
          P("Non-technical answer", H3),
          P(f"A put option is insurance: you pay a premium today, and if SM's price on the expiry date (70 trading days away) is below 95% of today's price you are paid the shortfall. We simulated 200,000 possible futures, including sudden jumps, and averaged the payouts. Most futures pay nothing; a minority pay a lot. "
            f"The premium is ${put['price']:.2f} and, with our 4% fee, ${put['client']:.2f}. Because the information we were given is noisy, we would hold a small reserve of about ${max(core)-min(core):.2f} per option."),
          PageBreak(), P("Step 3", H1), P("Question 3a: CIR model calibrated to the Euribor curve", H2), P("Technical answer", H3)]
ts = S3a["term_structure"]
table([[l, f"{s*100:.3f}", f"{d:.5f}", f"{z*100:.3f}"] for l, s, d, z in zip(ts["labels"], ts["simple"], ts["discount"], ts["zero"])], ["Maturity", "Euribor, simple (%)", "Discount factor", "Zero rate, continuous (%)"], "Euribor term structure.")
story.append(P("Process. Euribor quotes are simple money-market rates, so the discount factor is 1/(1+L t) and the continuously compounded zero rate is ln(1+L t)/t. A cubic spline through the five zero rates gives 52 weekly rates over 12 months. "
               "The CIR zero-coupon yield is fitted to these weekly rates by least squares, with the starting rate fixed at the one-week rate and the Feller condition 2 kappa theta >= sigma squared imposed."))
table([[f"{S3a['kappa']:.3f}", pct(S3a["theta"]), f"{S3a['sigma']:.3f}", f"{S3a['r0']:.3%}", f"{S3a['rmse_bp']:.2f}", f"{S3a['feller']:.3f}"]], ["Kappa", "Theta", "Sigma", "Start rate", "RMSE (bp)", "Feller margin"], "Calibrated CIR parameters.")


def cir_f():
    fg, a = plt.subplots(1, 3, figsize=(15, 4.2)); tt = np.array(S3a["t"]) * 12; pr = np.array(S3a["profile"])
    a[0].plot(np.array(ts["tau"]) * 12, np.array(ts["zero"]) * 100, "ro", label="Euribor zero rates"); a[0].plot(tt, np.array(S3a["spline"]) * 100, "g--", label="Cubic spline"); a[0].plot(tt, np.array(S3a["model"]) * 100, "b", label="CIR"); a[0].set(xlabel="Maturity (months)", ylabel="Zero rate (%)", title="CIR fit"); a[0].legend(fontsize=8)
    a[1].bar(tt, (np.array(S3a["spline"]) - np.array(S3a["model"])) * 1e4, width=.18); a[1].set(xlabel="Maturity (months)", ylabel="Spline minus CIR (bp)", title="Residuals")
    a[2].plot(pr[:, 0], pr[:, 3], "o-"); a[2].set(xlabel="Fixed sigma", ylabel="Best-fit RMSE (bp)", title="Sigma is not identified")
    for x in a: x.grid(alpha=.3)
    plt.tight_layout()


fig(cir_f, "CIR fit to the Euribor curve, residuals, and the flatness of the fit in sigma.")
no = S3a["near_optimal"]
story += [P(f"The model reproduces the curve with an RMSE of {S3a['rmse_bp']:.1f} basis points. Kappa ({S3a['kappa']:.2f}) and theta ({pct(S3a['theta'])}) are driven by the steep slope of the curve and extrapolate beyond 12 months; theta is therefore much higher than today's 12-month rate. "
            f"Sigma is essentially not identified by a yield curve: the fit is equally good for sigma between {S3a['plateau'][0]:.2f} and {S3a['plateau'][1]:.2f}, so we use the middle of that range and test sensitivity below. "
            f"Splining the quoted simple rates instead gives an RMSE of {S3a['simple_convention']['rmse_bp']:.1f} bp; letting the starting rate float lowers the RMSE to {S3a['free_r0']['rmse_bp']:.1f} bp but misses the one-week quote."),
          P("Non-technical answer", H3), P("We summarised the whole interest-rate curve with a three-setting model in which rates are pulled towards a long-run level. It tracks the curve closely. The curve tells us where rates are expected to go, but not how bumpy the path will be, which we explore separately."),
          P("Question 3b: 100,000 daily paths of the 12-month Euribor", H2), P("Technical answer", H3),
          P("Process. Using the exact CIR transition (non-central chi-square), we simulate 100,000 daily paths over 250 trading days. On every day the 12-month Euribor is the CIR one-year rate at the simulated short rate, converted back to a simple rate.")]


def sim_f():
    fg, a = plt.subplots(1, 2, figsize=(14, 4.3)); d = np.array(S3b["days"]); sm = np.array(S3b["samples"])
    for j in range(sm.shape[1]): a[0].plot(d, sm[:, j] * 100, lw=.5, alpha=.5)
    a[0].fill_between(d, np.array(S3b["lo95"]) * 100, np.array(S3b["hi95"]) * 100, color="k", alpha=.15, label="95% band"); a[0].plot(d, np.array(S3b["mean_path"]) * 100, "r", lw=2, label="Mean"); a[0].set(xlabel="Trading day", ylabel="12-month Euribor (%)", title="Simulated paths"); a[0].legend()
    h = S3b["hist"]; e = np.array(h["edges"]); a[1].bar((e[:-1] + e[1:]) / 2, h["counts"], width=e[1] - e[0]); a[1].axvline(S3b["expected"] * 100, c="r", ls="--", label="Expected"); a[1].axvline(S3b["current"] * 100, c="k", ls=":", label="Today")
    for x in S3b["conf"]["0.95"]: a[1].axvline(x * 100, c="purple", ls=":")
    a[1].set(xlabel="12-month Euribor in one year (%)", ylabel="Number of paths", title="Distribution after one year"); a[1].legend()
    for x in a: x.grid(alpha=.3)
    plt.tight_layout()


fig(sim_f, "Simulated 12-month Euribor paths with 95% band, and the distribution after one year (95% range dotted).")
cf = S3b["conf"]
table([[k_ + "%" if False else f"{float(k_):.0%}", pct(v[0]), pct(v[1])] for k_, v in cf.items()] + [["Absolute min / max of all paths", pct(S3b["min_all"]), pct(S3b["max_all"])]], ["Confidence", "Lower", "Upper"], "Range of the 12-month Euribor one year ahead.")
sd = S3b["sigma_sensitivity"]
table([[f"{s['sigma']:.2f}", pct(s["mean"]), pct(s["lo"]), pct(s["hi"])] for s in sd], ["Sigma", "Expected", "2.5th percentile", "97.5th percentile"], "Sensitivity of the one-year distribution to the unidentified sigma.")
imp = S3b["impact"]
table([[k_, pct(v["rate"]), f"{v['asian20']:.3f}", f"{v['put70']:.3f}", f"{v['discount_1y']:.4f}"] for k_, v in imp.items()], ["Rate used", "Rate", "Asian call 20d ($)", "Put 70d ($)", "1-year discount factor"], "Product prices at different rate levels (identical random numbers).")
dA = imp["Expected 12M in 1y"]["asian20"] - imp["Today 12M Euribor"]["asian20"]; dP = imp["Expected 12M in 1y"]["put70"] - imp["Today 12M Euribor"]["put70"]
story += [P(f"<b>(i) Range.</b> At 95% confidence the 12-month Euribor one year from now lies between <b>{pct(cf['0.95'][0])} and {pct(cf['0.95'][1])}</b> (90%: {pct(cf['0.90'][0])} to {pct(cf['0.90'][1])}; 99%: {pct(cf['0.99'][0])} to {pct(cf['0.99'][1])}). "
            f"Across the whole year the 95% band spans {pct(S3b['envelope']['95'][0])} to {pct(S3b['envelope']['95'][1])}, and the extreme simulated values are {pct(S3b['min_all'])} and {pct(S3b['max_all'])}. These widths scale with sigma, which the curve cannot identify (Table above): they should be read as scenario ranges."),
          P(f"<b>(ii) Expected value.</b> The expected 12-month Euribor in one year is <b>{pct(S3b['expected'])}</b> against {S3b['current']:.3%} today (an increase of {(S3b['expected']-S3b['current'])*1e4:.0f} basis points); {S3b['prob_above_current']:.1%} of paths end above today's level. "
            f"The expected value is insensitive to sigma, but it reflects the steep current curve extrapolated by the fitted model; other equally good fits give {pct(no['ev_min'])} to {pct(no['ev_max'])}. The model is fitted to today's prices, so this is a risk-neutral scenario, not a statistical forecast."),
          P(f"<b>(iii) Effect on pricing.</b> Moving from today's 12-month rate to the expected rate changes the 20-day Asian call by ${dA:+.3f} and the 70-day put by ${dP:+.3f}, and lowers the one-year discount factor from {imp['Today 12M Euribor']['discount_1y']:.4f} to {imp['Expected 12M in 1y']['discount_1y']:.4f}. "
            "A higher rate raises call values and lowers put values and discount factors. For these short-dated products the effect is small next to the volatility assumptions; for products with fixed-rate commitments or one-year funding it is material."),
          P("Non-technical answer", H3),
          P(f"If today's rate environment continues to evolve the way the curve suggests, the 12-month Euribor would be about {pct(S3b['expected'])} in a year, compared with {S3b['current']:.2%} today, and it is very likely (95%) to stay between {pct(cf['0.95'][0])} and {pct(cf['0.95'][1])}. "
            f"That higher rate would make our call options slightly more expensive (by about ${dA:.2f}) and our put options slightly cheaper (by about ${abs(dP):.2f}), and would reduce what a euro received in a year is worth today. The width of the range is an estimate: the curve alone cannot tell us how volatile rates will be."),
          P("Conclusion", H1),
          P(f"The 20-day at-the-money Asian call has a fair value of ${q['price']:.2f} and a client price of ${q['client']:.2f}. The 70-day put at 95% moneyness has a fair value of ${put['price']:.2f} and a client price of ${put['client']:.2f}. "
            f"The 12-month Euribor is expected to be {pct(S3b['expected'])} in one year, with a 95% range of {pct(cf['0.95'][0])} to {pct(cf['0.95'][1])}. "
            "The two main limitations are the put-call inconsistency in the supplied option quotes, which sets a floor under every fit and leaves individual Heston and Bates parameters weakly identified, and the fact that a 12-month yield curve cannot identify the volatility of the CIR rate. "
            "Prices are robust to these issues; parameters and rate ranges are not, and are reported with sensitivities."),
          P("References", H1)]
for ref in ["Andersen, Leif B. G. “Simple and Efficient Simulation of the Heston Stochastic Volatility Model.” <i>Journal of Computational Finance</i>, vol. 11, no. 3, 2008, pp. 1-42.",
            "Bates, David S. “Jumps and Stochastic Volatility: Exchange Rate Processes Implicit in Deutsche Mark Options.” <i>Review of Financial Studies</i>, vol. 9, no. 1, 1996, pp. 69-107.",
            "Carr, Peter, and Dilip Madan. “Option Valuation Using the Fast Fourier Transform.” <i>Journal of Computational Finance</i>, vol. 2, no. 4, 1999, pp. 61-73.",
            "Cox, John C., et al. “A Theory of the Term Structure of Interest Rates.” <i>Econometrica</i>, vol. 53, no. 2, 1985, pp. 385-407.",
            "Heston, Steven L. “A Closed-Form Solution for Options with Stochastic Volatility with Applications to Bond and Currency Options.” <i>Review of Financial Studies</i>, vol. 6, no. 2, 1993, pp. 327-43.",
            "Lewis, Alan L. “A Simple Option Formula for General Jump-Diffusion and Other Exponential Lévy Processes.” <i>SSRN</i>, 2001, papers.ssrn.com/sol3/papers.cfm?abstract_id=282110."]:
    story.append(P(ref, ParagraphStyle("r", parent=BODY, leftIndent=18, firstLineIndent=-18)))


def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.drawString(2 * cm, 1.2 * cm, "GROUP WORK PROJECT #1 - MScFE 622: Stochastic Modeling - Group 10290"); c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(d.page + 2)); c.restoreState()


body = TMP / "body.pdf"
SimpleDocTemplate(str(body), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm, title="MScFE 622 GWP1 - Answers", author="Group 10290").build(story, onFirstPage=footer, onLaterPages=footer)
w = PdfWriter(); orig = REPORT_DIR / "project_report_original_2025-07-24.pdf"
for pg in PdfReader(str(orig)).pages[:2]: w.add_page(pg)
for pg in PdfReader(str(body)).pages: w.add_page(pg)
out = REPORT_DIR / "GWP1_report.pdf"; w.write(str(out)); print("wrote", out, len(w.pages), "pages")
