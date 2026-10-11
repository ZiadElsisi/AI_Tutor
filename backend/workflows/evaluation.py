from backend.schemas import EvaluateResponse, QuestionFeedback, QuizQuestion


def evaluate(questions: list[QuizQuestion], answers: list[int | None]) -> EvaluateResponse:
    if len(answers) != len(questions):
        raise ValueError("Provide one answer for each question.")
    feedback, missed = [], []
    score = 0
    for question, answer in zip(questions, answers):
        correct = answer == question.correct_index
        score += int(correct)
        if not correct:
            missed.append(question.topic)
        feedback.append(QuestionFeedback(correct=correct, correct_index=question.correct_index,
            explanation=question.explanation, slide_refs=question.slide_refs, topic=question.topic))
    total = len(questions)
    return EvaluateResponse(score=score, total=total, percent=round(score * 100 / total, 1) if total else 0,
        feedback=feedback, suggested_review_topics=list(dict.fromkeys(missed)))
