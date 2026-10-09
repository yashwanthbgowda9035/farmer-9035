from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.database import db
from models.analysis import SoilRecord
from models.crop import CropPlot
from services.soil_service import soil_service

soil_bp = Blueprint("soil", __name__, url_prefix="/soil")

@soil_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    interpretation = None
    plots = CropPlot.query.filter_by(user_id=current_user.id).all()
    history = SoilRecord.query.filter_by(user_id=current_user.id).order_by(SoilRecord.created_at.desc()).all()
    
    if request.method == "POST":
        try:
            ph = float(request.form.get("ph", 6.5))
            nitrogen = float(request.form.get("nitrogen", 240))
            phosphorus = float(request.form.get("phosphorus", 18))
            potassium = float(request.form.get("potassium", 160))
            organic_carbon = float(request.form.get("organic_carbon", 0.55))
            ec = float(request.form.get("ec", 0.4))
            target_crop = request.form.get("target_crop", "Tomato")
            plot_id = request.form.get("plot_id")
            plot_id = int(plot_id) if plot_id and plot_id.isdigit() else None
            
            interpretation = soil_service.interpret_measurements(
                ph=ph,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                organic_carbon=organic_carbon,
                ec=ec,
                target_crop=target_crop
            )
            
            # Save record
            rec = SoilRecord(
                user_id=current_user.id,
                plot_id=plot_id,
                ph=ph,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                organic_carbon_pct=organic_carbon,
                electrical_conductivity=ec,
                status_summary=f"pH: {interpretation['measurements']['ph']['status']}",
                deficiency_tags=", ".join(interpretation["deficiencies"]) if interpretation["deficiencies"] else "Balanced",
                expert_advice="; ".join(interpretation["actionable_advisories"])
            )
            db.session.add(rec)
            db.session.commit()
            flash("Soil lab test saved and interpreted against ICAR benchmarks.", "success")
            
        except ValueError as e:
            flash(f"Invalid numerical input: {str(e)}", "danger")
            
    return render_template("soil.html", interpretation=interpretation, history=history, plots=plots)
