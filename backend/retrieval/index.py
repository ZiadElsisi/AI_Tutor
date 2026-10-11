import numpy as np


class LectureIndex:
    def __init__(self, passages: list[dict], embedder):
        if not passages:
            raise ValueError("No text passages to index.")
        self.passages = passages
        self.embedder = embedder
        self.vectors = np.asarray(embedder.encode([p["text"] for p in passages], normalize_embeddings=True))

    def search(self, query: str, k: int = 5) -> list[dict]:
        vector = np.asarray(self.embedder.encode([query], normalize_embeddings=True))[0]
        scores = self.vectors @ vector
        indices = np.argsort(scores)[::-1][:k]
        return [{**self.passages[int(i)], "score": float(scores[i])} for i in indices]
