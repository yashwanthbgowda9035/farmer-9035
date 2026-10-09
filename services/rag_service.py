import os
import json
from pathlib import Path
from pypdf import PdfReader
from models.database import db
from models.knowledge import KnowledgeDocument, KnowledgeChunk
from services.embedding_service import embedding_service
from config import Config

class RAGService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def chunk_text(self, text, chunk_size=350, overlap=50):
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_content = " ".join(words[start:end])
            chunks.append(chunk_content)
            if end == len(words):
                break
            start += chunk_size - overlap
        return chunks

    def ingest_document(self, file_path, title, author_source, doc_type="Manual", language="en"):
        path = Path(file_path)
        extracted_pages = []
        
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    extracted_pages.append((page_idx + 1, text.strip()))
        else: # TXT / MD
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                full_text = f.read()
            extracted_pages.append((1, full_text))
            
        if not extracted_pages:
            raise ValueError("No readable text found in document.")
            
        doc = KnowledgeDocument(
            title=title,
            author_source=author_source,
            doc_type=doc_type,
            file_path=str(path),
            language=language,
            is_indexed=True
        )
        db.session.add(doc)
        db.session.flush()
        
        total_chunks = 0
        for page_num, text in extracted_pages:
            chunks = self.chunk_text(text)
            for c_idx, c_text in enumerate(chunks):
                chunk_rec = KnowledgeChunk(
                    document_id=doc.id,
                    chunk_index=total_chunks,
                    page_number=page_num,
                    content=c_text,
                    token_count=len(c_text.split())
                )
                db.session.add(chunk_rec)
                total_chunks += 1
                
        doc.chunk_count = total_chunks
        db.session.commit()
        return doc

    def query(self, user_query, language="en", top_k=3, similarity_threshold=0.08):
        """
        Retrieves grounded evidence from indexed agricultural manuals.
        Supports English and Kannada queries.
        """
        # Kannada-English agricultural keyword bridging
        kannada_glossary = {
            "ಟೊಮ್ಯಾಟೊ": "tomato",
            "ಟೊಮೆಟೊ": "tomato",
            "ರೋಗ": "disease blight",
            "ಗೊಬ್ಬರ": "fertilizer nutrient NPK",
            "ನೀರು": "irrigation water requirement",
            "ಹುಳು": "pest insect borer",
            "ಬಿತ್ತನೆ": "sowing planting season",
            "ಇಳುವರಿ": "yield production harvest",
            "ಬೆಳೆ": "crop cultivation",
            "ಮಣ್ಣು": "soil test pH nutrients"
        }
        
        search_query = user_query
        for kn_word, en_trans in kannada_glossary.items():
            if kn_word in user_query:
                search_query += f" {en_trans}"
                
        # Query all knowledge chunks
        chunks = KnowledgeChunk.query.all()
        if not chunks:
            return {
                "status": "empty_knowledge_base",
                "answer": "The agricultural knowledge repository is currently empty. Please import verified extension publications via the Admin Knowledge portal.",
                "citations": [],
                "retrieved_chunks": []
            }
            
        chunk_texts = [c.content for c in chunks]
        similarities = embedding_service.compute_similarity(search_query, chunk_texts)
        
        scored_chunks = []
        for idx, score in enumerate(similarities):
            if score >= similarity_threshold:
                chunk = chunks[idx]
                doc = chunk.document
                scored_chunks.append({
                    "score": round(float(score), 4),
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "doc_title": doc.title,
                    "doc_author": doc.author_source,
                    "doc_type": doc.doc_type
                })
                
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_chunks = scored_chunks[:top_k]
        
        if not top_chunks:
            return {
                "status": "insufficient_evidence",
                "answer": "Insufficient agricultural evidence found in trusted documents to verify this question. KrishiMitra AI strictly adheres to verified source material and will not fabricate unsubstantiated agronomic claims.",
                "citations": [],
                "retrieved_chunks": []
            }
            
        # Grounded answer synthesis
        citations = []
        evidence_summary = []
        for ch in top_chunks:
            cite_str = f"[{ch['doc_title']}, {ch['doc_author']}, Page {ch['page_number']}]"
            citations.append(cite_str)
            # Take key sentences
            first_sentences = ". ".join(ch["content"].split(". ")[:3]) + "."
            evidence_summary.append(f"• From {cite_str}:\n  \"{first_sentences}\"")
            
        unique_citations = list(dict.fromkeys(citations))
        
        answer_text = (
            f"Based on verified agricultural extension publications:\n\n"
            + "\n\n".join(evidence_summary)
            + "\n\n⚠️ Disclaimer: Grounded strictly on repository documentation. For customized dosage or severe field outbreaks, consult your local Krishi Vigyan Kendra (KVK)."
        )
        
        if language == "kn":
            answer_text = (
                f"ಪರಿಶೀಲಿಸಿದ ಕೃಷಿ ವಿಸ್ತರಣಾ ಕೈಪಿಡಿಗಳ ಆಧಾರದ ಮೇಲೆ:\n\n"
                + "\n\n".join(evidence_summary)
                + "\n\n⚠️ ಗಮನಿಸಿ: ಈ ಮಾಹಿತಿಯು ನಮ್ಮ ದಾಖಲೆಗಳ ಆಧಾರದ ಮೇಲಿದೆ. ಹೆಚ್ಚಿನ ವಿವರಗಳಿಗೆ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು (KVK) ಸಂಪರ್ಕಿಸಿ."
            )
            
        return {
            "status": "success",
            "query": user_query,
            "language": language,
            "answer": answer_text,
            "citations": unique_citations,
            "retrieved_chunks": top_chunks
        }

rag_service = RAGService.get_instance()
