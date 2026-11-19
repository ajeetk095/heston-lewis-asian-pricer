import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
from ppt.make_deck import build, slides
setup('Presentation', '🎞️')
R_ = get_results(); st.title("Presentation (10 slides)")
st.download_button("Download PPTX", open(build(R_), 'rb').read(), "gwp1_deck.pptx")
for t, b in slides(R_): st.markdown(f"**{t}**\n\n{b}")
ai_panel("Presentation", None, ["Give me a 60-second pitch", "What questions will an examiner ask?"])
