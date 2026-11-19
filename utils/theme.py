"""Visual theme: CSS, Plotly template and small HTML components (hero, KPI cards, step cards)."""
import html
import plotly.graph_objects as go, plotly.io as pio

ACCENT, ACCENT2, BG, CARD, TEXT, MUTED = "#39D6C8", "#7C8CFF", "#0B1020", "#121A2B", "#E6EDF7", "#94A3B8"
COLORWAY = [ACCENT, "#7C8CFF", "#FFB454", "#FF6B8B", "#8BD17C", "#C792EA"]

CSS = f"""<style>
html, body, [class*="css"], [data-testid="stAppViewContainer"] {{ font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; }}
[data-testid="stAppViewContainer"] {{ background:radial-gradient(1200px 600px at 85% -10%, rgba(124,140,255,.14), transparent 60%),
    radial-gradient(900px 500px at -10% 0%, rgba(57,214,200,.10), transparent 55%), {BG}; }}
[data-testid="stHeader"] {{ background:transparent; }}
.block-container {{ padding-top:2.2rem; max-width:1250px; }}
h1 {{ font-weight:800!important; letter-spacing:-.02em; }}
h2, h3 {{ font-weight:700!important; letter-spacing:-.01em; }}
[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#0E1527,#0B1020); border-right:1px solid rgba(148,163,184,.14); }}
[data-testid="stSidebarNav"] a, [data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{ border-radius:10px; }}
.hero {{ position:relative; padding:2rem 2.2rem; border-radius:20px; overflow:hidden; color:#fff;
    background:linear-gradient(120deg,#0b6e6e 0%,#1b3a6b 55%,#3b2f7a 100%); border:1px solid rgba(255,255,255,.12);
    box-shadow:0 18px 50px rgba(0,0,0,.35); margin-bottom:1.2rem; }}
.hero:after {{ content:""; position:absolute; right:-60px; top:-60px; width:260px; height:260px; border-radius:50%;
    background:radial-gradient(circle,rgba(57,214,200,.35),transparent 70%); }}
.hero h1 {{ margin:0 0 .4rem 0; font-size:2rem; line-height:1.2; }}
.hero p {{ margin:0; opacity:.9; max-width:60rem; }}
.pill {{ display:inline-block; padding:.18rem .65rem; margin:.7rem .4rem 0 0; border-radius:999px; font-size:.75rem; font-weight:600;
    background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.2); }}
.kpi {{ background:{CARD}; border:1px solid rgba(148,163,184,.18); border-radius:16px; padding:1rem 1.1rem; height:100%;
    box-shadow:0 6px 20px rgba(0,0,0,.25); transition:transform .15s, border-color .15s; }}
.kpi:hover {{ transform:translateY(-2px); border-color:{ACCENT}; }}
.kpi .l {{ color:{MUTED}; font-size:.78rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }}
.kpi .v {{ font-size:1.9rem; font-weight:800; color:{TEXT}; margin:.15rem 0; }}
.kpi .s {{ color:{ACCENT}; font-size:.82rem; }}
.card {{ background:{CARD}; border:1px solid rgba(148,163,184,.18); border-radius:16px; padding:1rem 1.2rem; height:100%; }}
.card h4 {{ margin:.1rem 0 .35rem 0; font-size:1rem; }}
.card p {{ margin:0; color:{MUTED}; font-size:.88rem; line-height:1.45; }}
.step {{ display:inline-flex; width:28px; height:28px; align-items:center; justify-content:center; border-radius:50%;
    background:{ACCENT}; color:#04201e; font-weight:800; font-size:.85rem; margin-right:.5rem; }}
.tag {{ display:inline-block; padding:.1rem .55rem; border-radius:6px; font-size:.7rem; font-weight:700; margin-right:.35rem; }}
.t-high {{ background:rgba(57,214,200,.18); color:{ACCENT}; }} .t-med {{ background:rgba(255,180,84,.18); color:#FFB454; }}
.t-low {{ background:rgba(148,163,184,.18); color:{MUTED}; }} .t-rm {{ background:rgba(255,107,139,.18); color:#FF6B8B; }}
div[data-testid=stMetric] {{ border:1px solid rgba(148,163,184,.18); border-radius:14px; padding:.7rem .9rem; background:{CARD}; }}
.stTabs [data-baseweb="tab-list"] {{ gap:.3rem; }}
.stTabs [data-baseweb="tab"] {{ border-radius:10px 10px 0 0; padding:.5rem 1rem; }}
.stButton>button, .stDownloadButton>button {{ border-radius:10px; font-weight:600; }}
[data-testid=stExpander] {{ border-radius:12px; border:1px solid rgba(148,163,184,.18); }}
[data-testid=stDataFrame] {{ border-radius:12px; overflow:hidden; }}
.foot {{ color:{MUTED}; font-size:.72rem; line-height:1.4; }}
</style>"""

def _template():
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family="Inter, system-ui, sans-serif", color=TEXT), colorway=COLORWAY,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(18,26,43,.55)",
        xaxis=dict(gridcolor="rgba(148,163,184,.12)", zerolinecolor="rgba(148,163,184,.25)"),
        yaxis=dict(gridcolor="rgba(148,163,184,.12)", zerolinecolor="rgba(148,163,184,.25)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=40, r=20, t=55, b=40), title=dict(font=dict(size=16)),
        hoverlabel=dict(bgcolor=CARD))
    return t
pio.templates["gwp"] = _template(); pio.templates.default = "gwp"

def hero(title, text, pills=()):
    ps = "".join(f"<span class='pill'>{html.escape(p)}</span>" for p in pills)
    return f"<div class='hero'><h1>{html.escape(title)}</h1><p>{html.escape(text)}</p>{ps}</div>"
def kpi(label, value, sub=""):
    return f"<div class='kpi'><div class='l'>{html.escape(label)}</div><div class='v'>{html.escape(value)}</div><div class='s'>{html.escape(sub)}</div></div>"
def card(title, text, n=None, tags=""):
    num = f"<span class='step'>{n}</span>" if n is not None else ""
    return f"<div class='card'><h4>{num}{html.escape(title)}</h4>{tags}<p>{html.escape(text)}</p></div>"
def tag(kind, text):
    return f"<span class='tag t-{kind}'>{html.escape(text)}</span>"
