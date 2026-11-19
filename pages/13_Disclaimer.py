import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Disclaimer', '⚠️')
st.title("Disclaimer"); st.warning(DISC)

ai_panel("Disclaimer", None, ["What can and cannot this app be used for?"])
