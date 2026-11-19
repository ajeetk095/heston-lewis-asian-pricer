import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import *

setup("AI Assistant + Disclaimer", "🤖")
st.title("AI Assistant & Risk Disclaimer")
ensure()

st.warning(DISC)
st.markdown("This assistant combines the live Yahoo Finance snapshot, the app's Heston/Heston–Bates results, and the visitor's own parameters. It does not execute trades or guarantee outcomes.")

if not AI_ON():
    st.info("AI is switched off. Add OPENROUTER_API_KEY to Streamlit secrets or the OPENROUTER_API_KEY environment variable. The page remains available and no key is required for assignment calculations.")
else:
    ss.setdefault("chat", [])
    suggestions = [
        "Analyse the current market and model situation",
        "Give recommendations for a retail investor",
        "Give recommendations for a company treasury",
        "Give recommendations for a professional investor",
        "Explain the main risks and data limitations",
    ]
    chosen = st.pills("Suggested questions", suggestions, selection_mode="single")
    for message in ss.chat:
        st.chat_message(message["role"]).write(message["content"])

    question = st.chat_input("Ask about the live situation, model outputs or risk")
    if chosen and not question:
        question = chosen

    if question:
        ok, why = ai_allowed()
        if not ok:
            st.warning(why)
        else:
            question = clip(question, MAX_AI_CHARS)
            ss.chat.append({"role": "user", "content": question})
            st.chat_message("user").write(question)
            context = base_context("AI Assistant + Disclaimer", {"live_context": ss.get("home_live_context")})
            live = live_ctx()
            messages = [{"role": "system", "content": SYS + f"\nAPP STATE: {context}\nLIVE DATA: {live}"}] + ss.chat[-8:]
            with st.chat_message("assistant"):
                answer = st.write_stream(orc.stream_chat(messages))
            ss.chat.append({"role": "assistant", "content": answer})

    if ss.chat:
        if st.button("Clear conversation"):
            ss.chat = []
            st.rerun()
