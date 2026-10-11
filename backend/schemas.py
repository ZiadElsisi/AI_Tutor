from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Topic(StrictModel):
    name: str
    subtopics: list[str] = Field(default_factory=list)
    slide_refs: list[int] = Field(default_factory=list)


class LectureAnalysis(StrictModel):
    lecture_id: str
    title: str
    subject: str | None = None
    source_filename: str
    slide_count: int
    topics: list[Topic]
    learning_objectives: list[str]
    preview: str


class AskRequest(StrictModel):
    question: str = Field(min_length=2, max_length=2000)
    topic: str | None = Field(default=None, max_length=200)
    mode: Literal["simple", "detailed", "example", "summary"] = "detailed"
    history: list[dict[str, str]] = Field(default_factory=list, max_length=16)
    transcript: str | None = Field(default=None, max_length=12000)
    debug_retrieval: bool = False


class Citation(StrictModel):
    slide: int
    excerpt: str


class AskResponse(StrictModel):
    answer: str
    citations: list[Citation]
    grounded: bool
    supplementary_note: str | None = None
    retrieved_passages: list[str] | None = None


class QuizRequest(StrictModel):
    count: int = Field(default=5, ge=1, le=10)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    topic: str | None = Field(default=None, max_length=200)


class QuizQuestion(StrictModel):
    question: str
    options: list[str] = Field(min_length=2, max_length=6)
    correct_index: int = Field(ge=0)
    explanation: str
    difficulty: Literal["easy", "medium", "hard"]
    topic: str
    slide_refs: list[int] = Field(default_factory=list)

    @field_validator("correct_index")
    @classmethod
    def validate_index(cls, value: int, info):
        options = info.data.get("options")
        if options is not None and value >= len(options):
            raise ValueError("correct_index must refer to an available option")
        return value


class QuizResponse(StrictModel):
    quiz_id: str
    questions: list[QuizQuestion]


class EvaluateRequest(StrictModel):
    quiz_id: str
    answers: list[int | None]


class QuestionFeedback(StrictModel):
    correct: bool
    correct_index: int
    explanation: str
    slide_refs: list[int]
    topic: str


class EvaluateResponse(StrictModel):
    score: int
    total: int
    percent: float
    feedback: list[QuestionFeedback]
    suggested_review_topics: list[str]
