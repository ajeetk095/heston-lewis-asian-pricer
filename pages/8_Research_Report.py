import sys, os, io, zipfile; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ui import *
from utils.paths import REPORT_DIR, NOTEBOOK_DIR, DOC_DIR
setup('Research Report', '📄')
st.title("Report, notebook and downloads")
st.markdown("**Deliverables required by the brief (Step 4):** (1) a PDF containing only the answers, without code; (2) a zip with the executable Jupyter notebook and its HTML export.")
nb, html, pdf = NOTEBOOK_DIR/"GWP1_notebook.ipynb", NOTEBOOK_DIR/"GWP1_notebook.html", REPORT_DIR/"GWP1_report.pdf"
c = st.columns(3)
if pdf.exists(): c[0].download_button("⬇️ Report (PDF)", pdf.read_bytes(), pdf.name, "application/pdf")
if nb.exists() and html.exists():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z: z.write(nb, nb.name); z.write(html, html.name)
    c[1].download_button("⬇️ Notebook + HTML (zip)", buf.getvalue(), "GWP1_notebook_and_html.zip", "application/zip")
t = st.tabs(["Report (PDF)", "Notebook (HTML)", "Assignment brief", "Lewis (2001)", "Corrections & audit"])
with t[0]:
    pdf.exists() and pdf_view(pdf) or st.info("Report not found.")
with t[1]:
    if html.exists(): st.iframe(html, height=800)   # our own executed notebook export
    else: st.info("Notebook HTML not found.")
with t[2]: pdf_view(REPORT_DIR/"assignment_brief.pdf")
with t[3]: pdf_view(REPORT_DIR/"lewis_2001.pdf")
with t[4]: st.markdown((DOC_DIR/"CORRECTIONS.md").read_text())
ai_panel("Research Report", {"lewis_note": "Lewis (2001): C = S - sqrt(SK)e^{-rT}/pi * int Re[e^{iuk} phi(u-i/2)]/(u^2+1/4) du"}, ["Summarise Lewis (2001) in 5 bullets", "What are the main limitations of this project?"])
