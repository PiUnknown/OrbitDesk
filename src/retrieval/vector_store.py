class LocalVectorStore:
    def __init__(self, vectors, documents):
        self.vectors, self.documents, self.index = vectors, documents, None
        try:
            import faiss, numpy as np
            self.index = faiss.IndexFlatIP(len(vectors[0])); self.index.add(np.asarray(vectors, dtype="float32"))
        except Exception: pass
    def search(self, vector, k=5):
        if self.index is not None:
            import numpy as np
            _, indexes = self.index.search(np.asarray([vector], dtype="float32"), k)
            return [self.documents[i] for i in indexes[0] if i >= 0]
        return [self.documents[i] for _, i in sorted([(sum(a*b for a,b in zip(vector,row)), i) for i,row in enumerate(self.vectors)], reverse=True)[:k]]
