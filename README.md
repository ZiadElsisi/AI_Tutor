# AI Lecture Tutor

# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October) 2026

> 🎓 This project was built during the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

## 👤 Participant

| Field | Value |
| --- | --- |
| Full Name | Ziad Elsisi |
| Project Name | AI Lecture Tutor |
| GitHub Username | [ZiadElsisi](https://github.com/ZiadElsisi) |
| Internship Batch | August–October 2026 |
| Training Program | Large Language Models (LLMs) Program |
| Organization | [**Edrak for AI**](https://edrak4ai.com/en) |

---

## 📖 Project Overview

AI Lecture Tutor turns lecture slides into a guided study experience. Upload a text-based PDF or PowerPoint deck to extract its slide content, explore key topics, ask questions grounded in the material, and practice with quizzes.

The app uses retrieval-augmented generation (RAG): it retrieves relevant passages from the uploaded lecture and uses them to support tutor answers with slide citations. Lecture files and indexes are held in memory for the active session.

---

## ✨ Features

* Upload PDF and PPTX lecture slides and preserve slide references.
* Extract lecture topics and learning objectives.
* Ask questions about a lecture and receive answers with relevant slide citations.
* Generate quizzes at different difficulty levels and score answers.
* Track topics studied, quiz attempts, and progress in the current browser session.
* Use a Kaggle notebook to run the backend and app for a temporary, shareable demo.

---

## 🛠️ Technologies Used

* **Python** for the application and AI workflows.
* **Streamlit** for the user interface.
* **FastAPI** for the backend API.
* **Hugging Face Transformers** with **Qwen/Qwen3-1.7B** for text generation.
* **Sentence Transformers** with `all-MiniLM-L6-v2` for lecture embeddings.
* **NumPy** for vector retrieval.
* **PyMuPDF** and **python-pptx** for PDF and PowerPoint extraction.
* **Kaggle Notebooks** for the hosted demo runtime.
* **Cloudflare Quick Tunnel** for a temporary public app link during testing.

---

## ⚙️ Installation

### Kaggle demo

1. Open `backend/kaggle_demo.ipynb` from this repository in Kaggle.
2. Enable Internet in the notebook settings. Select a GPU accelerator if available.
3. Run the notebook cells from top to bottom. The first run installs dependencies and downloads the model files.
4. Open the app URL printed by the final cell.

The Kaggle app link is temporary. Keep the notebook session running while the instructor is testing; restarting the session creates a new link. Anyone with the link can access the app, and no instructor password is configured.

### Local development

Use Python 3.10 or newer with compatible ML package wheels. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

Start the API in one terminal:

```bash
export BACKEND_SECRET='choose-a-long-random-secret'
uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Start the Streamlit app in a second terminal with the same secret:

```bash
export BACKEND_URL='http://127.0.0.1:8000'
export BACKEND_SECRET='choose-a-long-random-secret'
streamlit run frontend/app.py
```

For local AI inference, load the model in the backend process with `backend.llm.runtime.runtime.load()`. Model weights are downloaded on first use and require several GB of storage; a GPU is recommended.

---

## 🚀 Usage

1. Open **Upload & Analyze** and enter a lecture title and subject.
2. Upload a text-based PDF or PPTX file and select **Analyze lecture**.
3. Review the extracted topics and learning objectives.
4. Open **Learning Workspace** to ask lecture questions or study a topic.
5. Use **Quiz & Assessment** to practice and **Progress & Review** to review quiz history.

Scanned image-only PDFs are not OCR processed. Uploading a new lecture or restarting the backend clears the backend's in-memory lecture data.

---

## 📸 Demo

Run [`backend/kaggle_demo.ipynb`](backend/kaggle_demo.ipynb) to generate a temporary URL for the app. The URL changes when the tunnel restarts and stops working when its Kaggle session or tunnel ends, so there is no permanent demo link.

---

## 📈 Results

The project delivers a working prototype that connects document ingestion, lecture retrieval, grounded tutoring, quiz generation, and progress tracking in one app. The backend is modular, and the Kaggle notebook runs the model and API in the same process so inference uses the loaded model.

---

## 🔮 Future Improvements

* Deploy to a stable host with predictable availability and a persistent URL.
* Add OCR for scanned lecture slides.
* Add durable storage for uploaded lectures and learning progress.
* Add instructor-controlled access for shared deployments.
* Expand evaluation of answer grounding, quiz quality, and response time.

---

## 📚 About the Internship

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**, and it will be showcased on the official [Tips Hindawi](https://www.tipshindawi.com/) website.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for AI**](https://edrak4ai.com/en), and the internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

## 📄 License

This project is shared for educational and portfolio purposes.
