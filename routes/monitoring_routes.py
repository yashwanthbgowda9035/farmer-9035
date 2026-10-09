import uuid
import cv2
import numpy as np
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.database import db
from models.crop import CropPlot, CropObservation
from config import Config

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/monitoring")

def estimate_leaf_canopy_coverage(image_path):
    """
    Computes green leaf canopy area percentage using HSV green segmentation.
    Returns estimated green percentage (0 - 100%).
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return 0.0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Green canopy mask
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = cv2.countNonZero(mask)
    total_pixels = img.shape[0] * img.shape[1]
    pct = (green_pixels / float(total_pixels)) * 100.0
    return round(pct, 1)

@monitoring_bp.route("/", methods=["GET"])
@login_required
def index():
    plots = CropPlot.query.filter_by(user_id=current_user.id).all()
    selected_plot_id = request.args.get("plot_id")
    selected_plot = None
    
    if selected_plot_id and selected_plot_id.isdigit():
        selected_plot = CropPlot.query.filter_by(id=int(selected_plot_id), user_id=current_user.id).first()
    elif plots:
        selected_plot = plots[0]
        
    observations = []
    if selected_plot:
        observations = CropObservation.query.filter_by(plot_id=selected_plot.id).order_by(CropObservation.observation_date.desc()).all()
        
    return render_template("monitoring.html", plots=plots, selected_plot=selected_plot, observations=observations)

@monitoring_bp.route("/plots/create", methods=["POST"])
@login_required
def create_plot():
    name = request.form.get("plot_name", "").strip()
    crop = request.form.get("crop_type", "Tomato").strip()
    variety = request.form.get("variety", "Hybrid").strip()
    acreage = float(request.form.get("acreage", 1.0))
    sowing_date_str = request.form.get("sowing_date")
    soil = request.form.get("soil_type", "Red Loam")
    irrigation = request.form.get("irrigation_system", "Drip")
    
    sowing_date = datetime.strptime(sowing_date_str, "%Y-%m-%d").date() if sowing_date_str else None
    
    if not name:
        flash("Plot name is required.", "warning")
        return redirect(url_for("monitoring.index"))
        
    plot = CropPlot(
        user_id=current_user.id,
        plot_name=name,
        crop_type=crop,
        variety=variety,
        acreage=acreage,
        sowing_date=sowing_date,
        soil_type=soil,
        irrigation_system=irrigation
    )
    db.session.add(plot)
    db.session.commit()
    flash(f"Plot '{name}' registered successfully.", "success")
    return redirect(url_for("monitoring.index", plot_id=plot.id))

@monitoring_bp.route("/observations/add", methods=["POST"])
@login_required
def add_observation():
    plot_id = request.form.get("plot_id")
    plot = CropPlot.query.filter_by(id=int(plot_id), user_id=current_user.id).first_or_404()
    
    stage = request.form.get("growth_stage", "Vegetative")
    height_str = request.form.get("plant_height_cm")
    height = float(height_str) if height_str else None
    notes = request.form.get("notes", "").strip()
    
    obs_filename = None
    leaf_area_pct = None
    
    if "observation_photo" in request.files:
        file = request.files["observation_photo"]
        if file.filename != "":
            ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
            obs_filename = f"obs_{uuid.uuid4().hex}.{ext}"
            save_path = Config.UPLOAD_FOLDER / obs_filename
            file.save(str(save_path))
            
            # Leaf area / green canopy coverage estimation
            leaf_area_pct = estimate_leaf_canopy_coverage(save_path)
            
    obs = CropObservation(
        plot_id=plot.id,
        observation_date=datetime.utcnow().date(),
        growth_stage=stage,
        plant_height_cm=height,
        estimated_leaf_area_index=leaf_area_pct,
        image_filename=obs_filename,
        notes=notes
    )
    db.session.add(obs)
    db.session.commit()
    
    flash("New growth observation recorded with canopy metric estimation.", "success")
    return redirect(url_for("monitoring.index", plot_id=plot.id))
