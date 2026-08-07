import hashlib
import time

class LocalEmbeddingModel:
    model_name = "BAAI/bge-small-en-v1.5"
    def __init__(self) -> None:
        started = time.perf_counter(); self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, local_files_only=True)
        except Exception: pass
        self.load_seconds = time.perf_counter() - started
    def encode(self, texts: list[str]) -> list[list[float]]:
        if self.model is not None: return self.model.encode(texts, normalize_embeddings=True).tolist()
        result = []
        for text in texts:
            vector = [0.0] * 128
            for token in text.lower().split(): vector[int(hashlib.sha256(token.encode()).hexdigest(), 16) % 128] += 1.0
            norm = sum(x*x for x in vector) ** .5 or 1.0
            result.append([x/norm for x in vector])
        return result
