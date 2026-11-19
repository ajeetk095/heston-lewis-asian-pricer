import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Learn', '🎓')
st.title("Learn How This Model Works")
st.markdown("""**1. Stochastic volatility.** Heston lets variance move: dS = rS dt + √v S dW₁, dv = κ(θ−v)dt + σ√v dW₂, corr ρ. ρ<0 gives the equity skew; σ gives smile curvature.

**2. Why Fourier (Lewis 2001).** The S-space density is awkward, but the characteristic function φ is closed-form. Option value = one integral of φ times the payoff transform (call: −K^{iz+1}/(z²−iz), Im z>1). With ν=½: C = S − √(SK)e^{−rT}/π ∫₀^∞ Re[e^{iuk} φ(u−i/2)]/(u²+¼) du.

**3. Calibration.** Data → model prices (puts by parity) → MSE → differential evolution + L-BFGS-B → sanity checks (Feller 2κθ ≥ σ², bounds, residuals, IV fit).

**4. Asian MC.** Payoff max(mean(S₀…S_T) − K, 0): S₀ is the first fixing, so n steps give n+1 points. Averaging lowers variance of the payoff → cheaper than vanilla.

**5. FAQ.** *Why not match the smile at 15 days?* One-factor Heston is too smooth for very short expiries; use jumps. *Why QE?* It handles low variance/Feller violations better than Euler.""")

ai_button("🤖 Quiz me (3 questions)", "Ask me 3 short multiple-choice questions on Heston dynamics, the Lewis formula and Asian options, with answers hidden until I reply. Start with question 1 only.", None, "Learn")
ai_panel("Learn", None, ["Explain the Heston model like I am 15", "Why does S0 belong in the Asian average?", "What does the Feller condition mean?"])
