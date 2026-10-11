from contextlib import asynccontextmanager
from hashlib import sha256
import os
import secrets
import uuid
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends
from backend.config import MAX_UPLOAD_BYTES, RETRIEVAL_K
from backend.ingestion.documents import extract_document, chunk_slides
from backend.retrieval.index import LectureIndex
from backend.schemas import LectureAnalysis, AskRequest, AskResponse, Citation, QuizRequest, QuizResponse, EvaluateRequest, EvaluateResponse
from backend.llm.runtime import runtime
from backend.workflows.lecture import analyze
from backend.workflows.tutor import answer as tutor_answer
from backend.workflows.quiz import generate as generate_quiz
from backend.workflows.evaluation import evaluate

lectures: dict[str, dict] = {}
document_cache: dict[str, dict] = {}
quizzes: dict[str, dict] = {}

def authenticate(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("BACKEND_SECRET", "")
    if not expected:
        raise HTTPException(503, "Backend authentication is not configured.")
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(401, "Invalid backend credentials.")

def require_model():
    if runtime.generator is None or runtime.embedder is None:
        raise HTTPException(503, "AI model is not loaded. Start the model cell in the notebook.")

def get_lecture(lecture_id: str) -> dict:
    item = lectures.get(lecture_id)
    if item is None:
        raise HTTPException(404, "Lecture not found. Notebook restarts clear temporary lectures; upload it again.")
    return item

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="AI Lecture Tutor API", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": runtime.generator is not None and runtime.embedder is not None,
            "device": runtime.device, "active_lectures": len(lectures)}

@app.post("/lectures/analyze", response_model=LectureAnalysis, dependencies=[Depends(authenticate)])
async def process_lecture(file: UploadFile = File(...), title: str = Form(...), subject: str = Form(default="")):
    require_model()
    filename = file.filename or "lecture"
    if not filename.lower().endswith((".pdf", ".pptx")):
        raise HTTPException(415, "Upload a PDF or PPTX file.")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File exceeds the 20 MiB upload limit.")
    digest = sha256(data).hexdigest()
    cached = document_cache.get(digest)
    try:
        if cached:
            slides, passages = cached["slides"], cached["passages"]
        else:
            slides = extract_document(filename, data)
            passages = chunk_slides(slides)
            if not passages:
                raise HTTPException(422, "No readable text was found. This may be an image-only document; OCR is not included.")
            document_cache[digest] = {"slides": slides, "passages": passages}
        lecture_id = str(uuid.uuid4())
        if cached and "index" in cached:
            index = cached["index"]
        else:
            index = LectureIndex(passages, runtime.embedder)
            document_cache[digest]["index"] = index
        result = analyze(title.strip() or filename, subject.strip() or None, passages,
                         len(slides), filename, lecture_id, runtime)
        lectures[lecture_id] = {"analysis": result, "index": index, "passages": passages}
        return result
    except HTTPException:
        raise
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, "Lecture processing failed. Check backend logs without sharing document contents.") from exc

@app.get("/lectures/{lecture_id}/topics", response_model=LectureAnalysis, dependencies=[Depends(authenticate)])
def topics(lecture_id: str):
    return get_lecture(lecture_id)["analysis"]

@app.post("/lectures/{lecture_id}/ask", response_model=AskResponse, dependencies=[Depends(authenticate)])
def ask(lecture_id: str, request: AskRequest):
    require_model()
    lecture = get_lecture(lecture_id)
    retrieved = lecture["index"].search(f"{request.topic or ''} {request.question}".strip(), RETRIEVAL_K)
    retrieved = [passage for passage in retrieved if passage["score"] >= 0.25]
    try:
        response = tutor_answer(request.question, request.topic, request.mode, request.history,
                                retrieved, request.transcript, runtime)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    citations = [Citation(slide=p["slide"], excerpt=p["text"][:320]) for p in retrieved]
    return AskResponse(answer=response, citations=citations, grounded=bool(retrieved),
        supplementary_note="The transcript was supplied by the student and was not independently verified." if request.transcript else None,
        retrieved_passages=[p["text"] for p in retrieved] if request.debug_retrieval else None)

@app.post("/lectures/{lecture_id}/quiz", response_model=QuizResponse, dependencies=[Depends(authenticate)])
def quiz(lecture_id: str, request: QuizRequest):
    require_model()
    lecture = get_lecture(lecture_id)
    passages = lecture["index"].search(request.topic or lecture["analysis"].title, max(RETRIEVAL_K, request.count))
    try:
        questions = generate_quiz(request.count, request.difficulty, request.topic, passages, runtime)
        quiz_id = str(uuid.uuid4())
        quizzes[quiz_id] = {"lecture_id": lecture_id, "questions": questions}
        return QuizResponse(quiz_id=quiz_id, questions=questions)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@app.post("/lectures/{lecture_id}/evaluate", response_model=EvaluateResponse, dependencies=[Depends(authenticate)])
def assess(lecture_id: str, request: EvaluateRequest):
    get_lecture(lecture_id)
    try:
        stored = quizzes.get(request.quiz_id)
        if stored is None or stored["lecture_id"] != lecture_id:
            raise HTTPException(404, "Quiz not found for this lecture.")
        return evaluate(stored["questions"], request.answers)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
