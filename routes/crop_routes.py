import os
import json
import uuid
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.database import db
from models.analysis import CropAnalysis, PestAnalysis
from services.disease_classifier import disease_classifier_service
from services.pest_classifier import pest_classifier_service
from services.rate_limiter import rate_limit
from config import Config

crop_bp = Blueprint("crop", __name__, url_prefix="/crop")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@crop_bp.route("/detect", methods=["GET"])
@login_required
def detect():
    model_configured = disease_classifier_service.is_configured()
    return render_template("detect.html", model_configured=model_configured)

@crop_bp.route("/detect/analyze", methods=["POST"])
@login_required
@rate_limit(limit=30, window_seconds=60)
def analyze():
    if "leaf_image" not in request.files:
        flash("Please select a leaf photograph to analyze.", "warning")
        return redirect(url_for("crop.detect"))
        
    file = request.files["leaf_image"]
    if file.filename == "":
        flash("No file was selected for upload.", "warning")
        return redirect(url_for("crop.detect"))
        
    if not allowed_file(file.filename):
        flash("Invalid file format. Please upload PNG, JPG, JPEG, or WEBP images.", "danger")
        return redirect(url_for("crop.detect"))
        
    # Generate secure non-predictable filename
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"leaf_{uuid.uuid4().hex}.{ext}"
    save_path = Config.UPLOAD_FOLDER / unique_filename
    file.save(str(save_path))
    
    # Run genuine computer vision inference
    result = disease_classifier_service.predict(save_path)
    
    if result.get("status") == "not_configured":
        return render_template("result.html", result=result, image_filename=unique_filename)
        
    if result.get("status") != "success":
        flash(result.get("error", "Error executing image inference."), "danger")
        return redirect(url_for("crop.detect"))
        
    # Persist analysis in database
    analysis = CropAnalysis(
        user_id=current_user.id,
        crop_type=result["crop"],
        image_filename=unique_filename,
        predicted_class=result["predicted_class"],
        confidence=result["confidence"],
        alternative_predictions=json.dumps(result["alternatives"]),
        heatmap_filename=result.get("heatmap_url"),
        recommendations=result.get("recommendations"),
        scientific_citations=result.get("citations"),
        model_version=result.get("model_version", "v1.0.0"),
        is_preliminary=True
    )
    db.session.add(analysis)
    db.session.commit()
    
    return render_template("result.html", result=result, analysis_id=analysis.id, image_filename=unique_filename)

@crop_bp.route("/result/<int:analysis_id>")
@login_required
def view_result(analysis_id):
    analysis = CropAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    result = {
        "status": "success",
        "crop": analysis.crop_type,
        "predicted_class": analysis.predicted_class,
        "confidence": analysis.confidence,
        "alternatives": analysis.get_alternatives(),
        "heatmap_url": analysis.heatmap_filename,
        "recommendations": analysis.recommendations,
        "citations": analysis.scientific_citations,
        "model_version": analysis.model_version,
        "is_preliminary": analysis.is_preliminary,
        "created_at": analysis.created_at.strftime("%Y-%m-%d %H:%M UTC")
    }
    return render_template("result.html", result=result, analysis_id=analysis.id, image_filename=analysis.image_filename)

@crop_bp.route("/pests", methods=["GET", "POST"])
@login_required
def pests():
    pest_result = None
    if request.method == "POST":
        if "pest_image" not in request.files or request.files["pest_image"].filename == "":
            flash("Please choose an insect/pest image.", "warning")
        else:
            file = request.files["pest_image"]
            if allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                fname = f"pest_{uuid.uuid4().hex}.{ext}"
                save_path = Config.UPLOAD_FOLDER / fname
                file.save(str(save_path))
                
                # Check dedicated pest service
                pest_result = pest_classifier_service.predict(save_path)
            else:
                flash("Invalid file format.", "danger")
                
    supported_species = pest_classifier_service.get_supported_species()
    return render_template("pests.html", pest_result=pest_result, supported_species=supported_species)
