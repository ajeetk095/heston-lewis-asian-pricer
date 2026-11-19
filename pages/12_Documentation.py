import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Documentation', '📚')
st.title("Documentation")
for f in ("deployment.md", "README.md", "documentation/CORRECTIONS.md"): st.markdown((ROOT/f).read_text())
ai_panel("Documentation", {"docs": (ROOT/"deployment.md").read_text()[:3000]}, ["My live data page shows demo mode - why?", "How do I add my API keys on Streamlit Cloud?"])
