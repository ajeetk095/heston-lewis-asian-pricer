import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
setup('Contact', '✉️')
st.title("Contact Developer")
n = clip(st.text_input("Name", max_chars=80), 80); e = clip(st.text_input("Email", max_chars=120), 120); msg = clip(st.text_area("Message", max_chars=1500), 1500)
if st.button("Send"):
    if not n.strip() or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e) or len(msg.strip()) < 10: st.error("Enter a name, a valid email and a message of ≥10 characters.")
    else:
        from urllib.parse import quote; st.success("Validated. Click to send via your mail client."); st.link_button("Open email", f"mailto:ajeetk095@gmail.com?subject={quote('Heston-Lewis app: '+n)}&body={quote(msg+chr(10)+e)}")
c = st.columns(3); c[0].link_button("Email","mailto:ajeetk095@gmail.com"); c[1].link_button("LinkedIn","https://www.linkedin.com/in/ajeek095/"); c[2].link_button("GitHub","https://github.com/ajeetk095")

ai_panel("Contact", None, ["Draft a polite message to the developer about a collaboration", "Draft a message asking for a feature"])
