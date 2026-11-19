import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.theme import CSS

st.set_page_config(page_title="SM Energy Pricer · MScFE 622 GWP1", page_icon="📈", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def page(filename, title, icon, default=False):
    url_name = filename.split("_", 1)[1][:-3].lower().replace("_", "-")
    return st.Page(f"pages/{filename}", title=title, icon=icon, url_path=url_name,
                   default=default)


pg = st.navigation([
    page("0_Home.py", "Home", "🏠", default=True),
    page("1_Live_Simulation.py", "Live Simulation", "📈"),
    page("3_AI_Explainability.py", "Model Diagnostics", "🔍"),
    page("4_Recommendations.py", "Recommendations", "💡"),
    page("5_Real_Time_Data.py", "Real-Time Data", "📡"),
    page("7_Learn.py", "Learn", "🎓"),
    page("14_Roadmap.py", "Roadmap & Suggestions", "🧭"),
    page("2_Assignment_Tasks.py", "Assignment Tasks", "📝"),
    page("8_Research_Report.py", "Report & Downloads", "📄"),
    page("9_Presentation.py", "Presentation", "🎞️"),
], expanded=True)
pg.run()
