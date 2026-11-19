# Deployment

The app needs no secrets to show the assignment results (pre-computed in `results/gwp1_results.json`; if that file is missing it recomputes a quick version on first load). Python 3.11+.

**Streamlit Community Cloud (simplest, free):** push this folder to a GitHub repository → share.streamlit.io → *New app* → repository, branch `main`, main file `app.py` → *Advanced settings* → Python 3.11. Optional secrets: `OPENROUTER_API_KEY`, `FRED_API_KEY`. Do not commit secrets.

**Docker (any host):**
```bash
docker build -t gwp1-app .
docker run -p 8501:8501 gwp1-app            # add --env-file .env for optional API keys
# health check: curl http://localhost:8501/_stcore/health  -> ok
```
The image runs as a non-root user, honours `$PORT` (Render, Railway, Cloud Run) and has a built-in health check.

**Render / Railway / Heroku-style:** the `Procfile` starts `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`; `runtime.txt` pins Python 3.11.9.

**Hugging Face Spaces:** create a Streamlit Space, upload the files, add secrets in Settings.

**Checks before going live:** `pytest` (≈2 min incl. all pages), then open the Assignment Tasks page and confirm the headline numbers equal the notebook's final cell.

**Troubleshooting:** yfinance rate limits make the Real-Time page fall back to demo data; the assistant shows a generic error if the OpenRouter key is missing. Calibrating live on the sandbox page takes 20–60 s.
