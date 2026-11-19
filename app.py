import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from utils.theme import CSS
st.set_page_config(page_title="SM Energy Pricer · MScFE 622 GWP1", page_icon="📈", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
P = lambda f, t, i, **k: st.Page(f"pages/{f}", title=t, icon=i, url_path=f.split("_",1)[1][:-3].lower().replace("_","-") if not k else "", **k)
pg = st.navigation({
    "Overview": [P("0_Home.py", "Home", "🏠", default=True), P("14_Roadmap.py", "Roadmap & Suggestions", "🧭")],
    "Assignment": [P("2_Assignment_Tasks.py", "Assignment Tasks", "📝"), P("8_Research_Report.py", "Report & Downloads", "📄"), P("9_Presentation.py", "Presentation", "🎞️")],
    "Explore": [P("1_Live_Simulation.py", "Live Simulation", "📈"), P("3_AI_Explainability.py", "Model Diagnostics", "🔍"), P("4_Recommendations.py", "Recommendations", "💡"),
                P("5_Real_Time_Data.py", "Real-Time Data", "📡"), P("7_Learn.py", "Learn", "🎓")],
    "Extras": [P("6_AI_Assistant.py", "AI Assistant", "🤖")],
    "About": [P("12_Documentation.py", "Documentation", "📚"), P("10_About_Developer.py", "About Developer", "👤"), P("11_Contact.py", "Contact", "✉️"), P("13_Disclaimer.py", "Disclaimer", "⚠️")],
}, expanded=True)
pg.run()
