import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('About Developer', '👤')
st.title("Ajeet Kumar"); st.image("assets/profile.png", width=160) if os.path.exists("assets/profile.png") else None
st.write("Quantitative finance aspirant, Bangalore. B.Tech IT (AKTU); M.Tech CSE (NSUT, CGPA 7.92); M.Sc. Financial Engineering, WorldQuant University (88%). Python, C++, SQL; MVO, Black-Litterman, Monte Carlo, ML. 1st place Algo8 ML Hackathon (IIT Kanpur); felicitated by the President of India.")
st.write("**Skills:** AI · ML · Data Science · Computer Vision · RL · Portfolio Optimization · Quantitative Finance · Stochastic Modeling · Python · SQL")
st.write("**Journey:** Idea → Research (Lewis 2001) → Data (SM option chain) → Calibration → Asian pricing → Live deployment → Future vision (Lévy/jump models)")
c = st.columns(3); c[0].link_button("LinkedIn","https://www.linkedin.com/in/ajeek095/"); c[1].link_button("GitHub","https://github.com/ajeetk095"); c[2].link_button("Email","mailto:ajeetk095@gmail.com")

ai_panel("About Developer", {"bio": "Ajeet Kumar, quant finance aspirant, Bangalore; M.Sc. Financial Engineering (WorldQuant); Python/C++/SQL"}, ["Why is this project a good portfolio piece?", "How would you explain this to a recruiter?"])
