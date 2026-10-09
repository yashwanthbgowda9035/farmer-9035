import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        # Local semantic vectorizer with sublinear scaling and character/word n-grams
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
            max_features=5000
        )
        self.is_fitted = False
        self.corpus = []
        
    def fit_or_update(self, text_chunks):
        if not text_chunks:
            return
        self.corpus = text_chunks
        self.vectorizer.fit(text_chunks)
        self.is_fitted = True
        
    def compute_similarity(self, query, chunk_texts):
        if not self.is_fitted or not chunk_texts:
            # Fit on available chunks + query
            combined = chunk_texts + [query]
            vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
            tfidf_matrix = vec.fit_transform(combined)
            query_vec = tfidf_matrix[-1]
            chunk_vecs = tfidf_matrix[:-1]
            sims = cosine_similarity(query_vec, chunk_vecs)[0]
            return sims.tolist()
            
        q_vec = self.vectorizer.transform([query])
        chunk_vecs = self.vectorizer.transform(chunk_texts)
        sims = cosine_similarity(q_vec, chunk_vecs)[0]
        return sims.tolist()

embedding_service = EmbeddingService.get_instance()
