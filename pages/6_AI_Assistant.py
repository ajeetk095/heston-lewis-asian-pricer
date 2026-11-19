import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup("AI Assistant", "🤖")
st.title("AI Assistant – Ask the Model")
if not AI_ON():
    st.info("The AI assistant is optional and switched off because no OPENROUTER_API_KEY is configured. Everything required by the assignment works without it. Add the key in Streamlit secrets to enable it.")
    st.stop()
st.warning("Assistant responses are not professional or investment advice.")
ensure()
SUG = ["Explain the Lewis formula in plain language", "Interpret my latest pricing result", "How can I improve the calibration?", "What is SM's price and VIX right now?", "Latest news on SM Energy"]
ss.setdefault("chat", [])
c = st.columns(len(SUG)); pick = None
for i, s in enumerate(SUG):
    if c[i].button(s, key=f"s{i}"): pick = s
q = st.chat_input("Ask about the project, the app or the market", max_chars=MAX_AI_CHARS) or pick
q = clip(q, MAX_AI_CHARS) if q else q
for m in ss.chat: st.chat_message(m["role"]).write(m["content"])
def tools(text):
    t = text.lower(); out = {}
    try:
        if any(w in t for w in ("price","spot","now","today","trading","sm ")): out["spot"] = ld.spot()
        if any(w in t for w in ("vix","market","s&p","volatil","condition")): out["market"] = ld.market_context()
        if any(w in t for w in ("rate","fred","treasury","discount")): out["risk_free"] = ld.risk_free()
        if "news" in t or "headline" in t: out["news"] = ld.news()
        if any(w in t for w in ("chain","strike","skew","smile","option")):
            e = ld.expiries(); out["expiries"] = e[:6]; out["chain_head"] = ld.chain(e[0]).head(12).to_dict("records") if e else []
    except Exception as e: out["fetch_error"] = f"{type(e).__name__}: {e}"
    return out
if q:
    ok, why = ai_allowed()
    if not ok: st.warning(why); st.stop()
    st.chat_message("user").write(q); ss.chat.append({"role": "user", "content": q})
    with st.spinner("Fetching live data…"): fetched = tools(q)
    sys_ = SYS + f"\nAPP STATE: {base_context('AI Assistant')}\nLIVE DATA: {live_ctx()}\nON-DEMAND FETCH: {json.dumps(fetched, default=str)[:4000]}"
    msgs = [{"role": "system", "content": sys_}] + ss.chat[-8:]
    with st.chat_message("assistant"): out = st.write_stream(orc.stream_chat(msgs, ss.model_id))
    ss.chat.append({"role": "assistant", "content": out})
if ss.chat and st.button("Clear chat"): ss.chat = []; st.rerun()
