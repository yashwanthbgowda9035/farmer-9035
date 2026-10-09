import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.database import db
from models.knowledge import KnowledgeDocument, KnowledgeChunk
from services.rag_service import rag_service
from config import Config

knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/knowledge")

@knowledge_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    query_result = None
    query_text = ""
    language = request.args.get("lang", current_user.preferred_language or "en")
    
    if request.method == "POST":
        query_text = request.form.get("query", "").strip()
        language = request.form.get("language", language)
        if query_text:
            query_result = rag_service.query(query_text, language=language)
            
    documents = KnowledgeDocument.query.order_by(KnowledgeDocument.created_at.desc()).all()
    total_chunks = KnowledgeChunk.query.count()
    
    return render_template(
        "knowledge.html",
        documents=documents,
        total_chunks=total_chunks,
        query_result=query_result,
        query_text=query_text,
        language=language
    )

@knowledge_bp.route("/import", methods=["POST"])
@login_required
def import_document():
    if not current_user.is_admin:
        flash("Unauthorized. Only administrators can import agricultural reference documents.", "danger")
        return redirect(url_for("knowledge.index"))
        
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "ICAR / UAS").strip()
    doc_type = request.form.get("doc_type", "Manual")
    
    if "document_file" not in request.files:
        flash("No file selected.", "warning")
        return redirect(url_for("knowledge.index"))
        
    file = request.files["document_file"]
    if file.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("knowledge.index"))
        
    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    if ext not in Config.ALLOWED_DOC_EXTENSIONS:
        flash("Allowed document types: PDF, TXT, MD.", "danger")
        return redirect(url_for("knowledge.index"))
        
    filename = secure_filename(file.filename)
    save_path = Config.UPLOAD_FOLDER / filename
    file.save(str(save_path))
    
    try:
        doc = rag_service.ingest_document(save_path, title or filename, author, doc_type=doc_type)
        flash(f"Document '{doc.title}' imported and indexed into {doc.chunk_count} vector chunks.", "success")
    except Exception as e:
        flash(f"Error processing document: {str(e)}", "danger")
        
    return redirect(url_for("knowledge.index"))
