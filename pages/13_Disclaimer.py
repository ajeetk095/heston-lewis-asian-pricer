import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import *
setup("Disclaimer", "⚠️")
st.title("Risk Disclaimer")
st.warning(DISC)
st.markdown("For the merged market assistant and advice context, open the AI Assistant on the Home page or use the Home-page assistant panel.")
