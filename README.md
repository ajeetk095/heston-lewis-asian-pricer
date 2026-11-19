# Heston–Lewis Options Pricer (MScFE 622 GWP1)

Streamlit app, executable notebook and report for MScFE 622 Group Work Project 1: Heston and Bates calibration (Lewis 2001, Carr–Madan 1999), Asian-call and put Monte Carlo, and CIR/Euribor scenarios.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py          # opens on http://localhost:8501
```
The app loads pre-computed results from `results/gwp1_results.json`, so it starts instantly. Refresh them with `python -m utils.pipeline` (about 10–15 minutes on two cores; `--quick` for a smoke test). API keys (OpenRouter, FRED) are optional and only used by the assistant and real-time pages.

## Deliverables (brief, Step 4)
| File | Content |
|---|---|
| `reports/GWP1_report.pdf` | Answers only (no code), technical + non-technical, MLA references; pages 1–2 are the group's filled template |
| `notebooks/GWP1_notebook.ipynb` + `.html` | Self-contained executable notebook (library inlined, data embedded as fallback) |
| `dist/GWP1_notebook_and_html.zip` | The zip to upload |
| `pages/2_Assignment_Tasks.py` | Every question answered in the app, with graphs |
| `documentation/CORRECTIONS.md` | What was wrong in the earlier version and how it was fixed |

## Rebuild everything
```bash
pip install -r requirements-dev.txt
python -m utils.pipeline                       # results JSON used by the app and the report
python build_notebook.py && jupyter nbconvert --to notebook --execute --inplace notebooks/GWP1_notebook.ipynb \
  && jupyter nbconvert --to html notebooks/GWP1_notebook.ipynb
python scripts/build_report.py                 # PDF
pytest
```

## Deployment
See `deployment.md` (Streamlit Community Cloud, Docker, Render, Hugging Face Spaces). Keep keys in environment variables or Streamlit secrets.

**References:** Heston (1993); Lewis (2001); Carr & Madan (1999); Bates (1996); Andersen (2008); Cox, Ingersoll & Ross (1985).

**Disclaimer:** For research and education only; not financial or investment advice.
