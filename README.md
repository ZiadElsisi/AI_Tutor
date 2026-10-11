# AI Lecture Tutor

A learning app with a Streamlit frontend and FastAPI backend. The backend loads an open-weight model, extracts PDF/PPTX slides, retrieves lecture passages, answers with slide citations, generates validated quizzes, and scores answers deterministically.

## Free demonstration setup

- **Google Colab**: a Google account is required. GPU access, session duration, and storage vary and are not guaranteed. A disconnected runtime stops inference and clears in-memory lecture data. The notebook runs the API only on localhost for notebook-local calls. Google's current [Colab FAQ](https://research.google.com/colaboratory/faq.html) disallows unrelated web service offerings from managed runtimes, so this project does not tunnel or publish Colab's FastAPI service.
- **Frontend hosting**: deploy the Streamlit app to Streamlit Community Cloud (GitHub account/repository and Streamlit account). The UI reads `BACKEND_URL` and `BACKEND_SECRET` from server-side secrets. Never put the secret in source or browser-visible output.
- **Remote backend hosting**: a separately hosted public FastAPI service is required for the hosted frontend. This repository does not provision one. Hugging Face documents Docker/FastAPI Spaces, but currently says compute-backed Docker/Gradio Spaces require a paid plan; that is outside the free-only setup. No paid host or API is silently selected. A permitted free backend host is not guaranteed by the free tiers documented here; until one is configured, the public frontend intentionally reports offline.
- **Model**: default `Qwen/Qwen3-1.7B` ([Apache-2.0 model card](https://huggingface.co/Qwen/Qwen3-1.7B)). It needs multiple GB of download/storage and is best used with an available notebook GPU. CPU fallback is supported but can be very slow; set `MODEL_ID` to another compatible instruct model if needed. Model weights are not downloaded until the notebook's model-loading cell runs.
- No paid API is used or silently substituted. Embeddings use `sentence-transformers/all-MiniLM-L6-v2`; it also downloads model files on first load.

## Local development

Use Python 3.10 or 3.11 (Python 3.14 does not currently have dependable wheels for the full ML dependency stack).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
export BACKEND_SECRET='replace-with-a-long-random-secret'
uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

The API starts without loading model weights. `/health` reports `model_loaded: false`; inference endpoints return `503` until a model is loaded. To run the full model locally for development, install backend requirements and set `MODEL_ID`, then call `backend.llm.runtime.runtime.load()`.

In a second terminal:

```bash
source .venv/bin/activate
export BACKEND_URL=http://127.0.0.1:8000
export BACKEND_SECRET='replace-with-a-long-random-secret'
streamlit run frontend/app.py
```

## Colab backend

Open `backend/notebook.ipynb` in Google Colab and run cells in order. It installs dependencies, asks for a shared secret using a hidden prompt, loads the model, and starts FastAPI on localhost for requests from the notebook runtime. It does not expose a public URL. Restarting the runtime requires re-running setup and clears temporary lectures. To connect a hosted frontend, deploy the backend on a host that permits public inference services and configure its URL and shared secret in frontend hosting settings.

## Kaggle instructor demo

Use `backend/kaggle_demo.ipynb` for a one-link, temporary demo. It loads the model and runs FastAPI in the same Python process so the API can use the loaded model, runs Streamlit separately, then creates a Cloudflare Quick Tunnel to the Streamlit UI. The notebook prints one temporary URL to share with the instructor; the API stays on localhost and the instructor does not need source code or a Kaggle login. No instructor password is configured. Anyone who obtains the temporary URL can use the demo, so share it only with the instructor.

This is a short live demo, not an always-on host. Keep the Kaggle notebook session active during the test. If Kaggle ends the session, the link stops working and uploaded lecture data is lost. Restarting the tunnel creates a different URL. Kaggle GPU/internet availability and third-party tunnel connectivity are not guaranteed; the [Kaggle notebook docs](https://www.kaggle.com/docs/notebooks) describe interactive compute sessions, while [Cloudflare describes Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/) as temporary testing/development tunnels. Check Kaggle's current terms before relying on this arrangement for a formal or unattended deployment.

## Deployment

1. Push this repository to GitHub.
2. On Streamlit Community Cloud, create an app pointing at `frontend/app.py` (root `requirements.txt` installs the frontend dependencies).
3. For a one-person live demo, use the Kaggle instructor-demo steps above.
4. For a local end-to-end demo, start FastAPI and Streamlit using the local commands above. Set `BACKEND_URL=http://127.0.0.1:8000` and the same `BACKEND_SECRET` in the frontend process environment.
5. For a public frontend demo, first configure a permitted remote FastAPI host. Then add its `BACKEND_URL` and `BACKEND_SECRET` to the frontend host's server-side Secrets. The app checks backend health and shows recovery instructions if it is unavailable.

## API and data handling

All protected endpoints use `X-API-Key`. Uploads are limited to 20 MiB and PDF/PPTX only. Each analysis receives an opaque lecture ID and its own in-memory vector index. Conversation history, topic completion, and quiz history live in the Streamlit browser session. There is no cross-user or durable database. Restarting a backend clears uploaded documents and indexes; restarting the browser session may clear UI history. No document text or credentials are logged. Compute is shared and no distributed rate limiter is included, so the API is not designed for unrestricted public traffic.

YouTube recommendations are generated as search links, not fabricated video results. Users can paste a YouTube URL for supported embedding, or add transcript text themselves. No videos are downloaded, and no transcript is presumed available. Timestamp suggestions are not generated.

## Evaluation

Run the repeatable local checks with `pytest -q` after installing `backend/requirements.txt` and `tests/requirements.txt`. Checks use synthetic fixtures and do not download a model. Live generation, hosted frontend deployment, Colab GPU access, and tunnel availability require manual demonstration setup; no accuracy or latency claim is made here.

## Limitations

- Scanned/image-only PDFs have no OCR; an empty extraction is reported with guidance.
- Model output quality and latency depend on the selected model and available GPU/CPU memory.
- Free hosting, notebook GPU allocation, runtime duration, remote inference availability, and storage are not guaranteed.
- Quick Tunnel URLs are temporary. Never expose the secret or share a public inference URL as an unlimited service.
