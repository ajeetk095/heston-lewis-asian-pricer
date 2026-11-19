import numpy as np
def heston_cf(z, T, v0, kappa, theta, sigma, rho):
    """E[exp(i z X_T)], X_T = ln(S_T/F_T). Stable 'little trap' form; z may be complex."""
    b = kappa - rho*sigma*1j*z
    d = np.sqrt(b**2 + sigma**2*(1j*z + z**2))
    g = (b - d)/(b + d)
    e = np.exp(-d*T)
    C = (kappa*theta/sigma**2)*((b - d)*T - 2*np.log((1 - g*e)/(1 - g)))
    D = ((b - d)/sigma**2)*((1 - e)/(1 - g*e))
    return np.exp(C + D*v0)
