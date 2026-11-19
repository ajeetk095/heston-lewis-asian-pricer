import os, requests, pandas as pd, streamlit as st
@st.cache_data(ttl=60)
def spot(tk="SM"):
    import yfinance as yf
    return float(yf.Ticker(tk).history(period="5d")['Close'].iloc[-1])
@st.cache_data(ttl=300)
def expiries(tk="SM"):
    import yfinance as yf; return list(yf.Ticker(tk).options)
@st.cache_data(ttl=300)
def chain(expiry, tk="SM"):
    import yfinance as yf
    c = yf.Ticker(tk).option_chain(expiry)
    d = pd.concat([c.calls.assign(Type='C'), c.puts.assign(Type='P')])
    d['Price'] = (d['bid']+d['ask'])/2
    return d[(d['bid']>0)&(d['ask']>0)][['strike','Price','Type','impliedVolatility']].rename(columns={'strike':'Strike'})
@st.cache_data(ttl=3600)
def risk_free(default=0.015):
    key = os.environ.get("FRED_API_KEY")
    if not key:
        try: key = st.secrets["FRED_API_KEY"]
        except Exception: key = None
    try:
        if key:
            j = requests.get("https://api.stlouisfed.org/fred/series/observations", timeout=8, params=dict(
                series_id="DGS3MO", api_key=key, file_type="json", sort_order="desc", limit=5)).json()
            for o in j["observations"]:
                if o["value"] != ".": return float(o["value"])/100
    except Exception: pass
    return default
@st.cache_data(ttl=300)
def market_context():
    import yfinance as yf; out = {}
    for n,t in {"SPX":"^GSPC","VIX":"^VIX","TNX":"^TNX"}.items():
        try: out[n] = float(yf.Ticker(t).history(period="5d")['Close'].iloc[-1])
        except Exception: out[n] = None
    return out
@st.cache_data(ttl=600)
def news(tk="SM", n=5):
    import yfinance as yf
    out = []
    for it in (yf.Ticker(tk).news or [])[:n]:
        c = it.get("content", it); out.append({"title": str(c.get("title") or "")[:200], "publisher": str((c.get("provider") or {}).get("displayName") or "")[:60]})
    return out
@st.cache_data(ttl=3600)
def dividend_yield(tk="SM"):
    import yfinance as yf
    try:
        y = yf.Ticker(tk).info.get("dividendYield") or 0.0; return float(y/100 if y > 0.5 else y)
    except Exception: return 0.0
