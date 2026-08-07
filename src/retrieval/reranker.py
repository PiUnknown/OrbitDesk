def rerank(query, documents, k=3):
    terms = set(query.lower().split())
    return sorted(documents, key=lambda d: len(terms & set(d["text"].lower().split())), reverse=True)[:k]
