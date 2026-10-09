from datetime import datetime
from models.database import db

class KnowledgeDocument(db.Model):
    __tablename__ = "knowledge_documents"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author_source = db.Column(db.String(255), default="ICAR / UAS Bangalore / Karnataka Dept of Agriculture")
    doc_type = db.Column(db.String(50), default="Manual") # Manual, Research Paper, Advisory, Extension Bulletin
    file_path = db.Column(db.String(255), nullable=True)
    language = db.Column(db.String(10), default="en") # en or kn
    chunk_count = db.Column(db.Integer, default=0)
    is_indexed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chunks = db.relationship("KnowledgeChunk", backref="document", lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeDocument {self.title}>"

class KnowledgeChunk(db.Model):
    __tablename__ = "knowledge_chunks"
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    page_number = db.Column(db.Integer, default=1)
    content = db.Column(db.Text, nullable=False)
    embedding_json = db.Column(db.Text, nullable=True) # Vector stored as JSON list of floats
    token_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<KnowledgeChunk doc={self.document_id} chunk={self.chunk_index}>"
