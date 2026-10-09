from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.database import db
from models.user import User
from models.crop import CropPlot
from models.analysis import CropAnalysis, SoilRecord
from models.notification import ReminderAlert
from services.weather_service import weather_service
from services.risk_analysis import risk_analysis_service

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    plots = CropPlot.query.filter_by(user_id=current_user.id).all()
    recent_analyses = CropAnalysis.query.filter_by(user_id=current_user.id).order_by(CropAnalysis.created_at.desc()).limit(5).all()
    soil_tests = SoilRecord.query.filter_by(user_id=current_user.id).order_by(SoilRecord.created_at.desc()).limit(3).all()
    reminders = ReminderAlert.query.filter_by(user_id=current_user.id, is_read=False).order_by(ReminderAlert.created_at.desc()).all()
    
    # Weather glance
    weather = weather_service.get_weather()
    weather_risk = None
    if weather.get("status") == "success":
        weather_risk = risk_analysis_service.evaluate_risk(
            crop_type="Tomato",
            growth_stage="Vegetative",
            temperature_c=weather["temperature_c"],
            humidity_pct=weather["humidity_pct"],
            rainfall_mm=weather["rainfall_mm"]
        )
        
    return render_template(
        "dashboard.html",
        plots=plots,
        recent_analyses=recent_analyses,
        soil_tests=soil_tests,
        reminders=reminders,
        weather=weather,
        weather_risk=weather_risk
    )

@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        language = request.form.get("preferred_language", "en")
        location = request.form.get("location", "").strip()
        phone = request.form.get("phone", "").strip()
        
        current_user.preferred_language = language
        if location:
            current_user.state_district = location
        current_user.phone = phone
        db.session.commit()
        
        flash("Profile settings updated successfully.", "success")
        return redirect(url_for("main.settings"))
        
    return render_template("settings.html")

@main_bp.route("/history")
@login_required
def history():
    analyses = CropAnalysis.query.filter_by(user_id=current_user.id).order_by(CropAnalysis.created_at.desc()).all()
    return render_template("history.html", analyses=analyses)

@main_bp.route("/alerts", methods=["GET", "POST"])
@login_required
def alerts():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        category = request.form.get("category", "Observation")
        
        if title and message:
            alert = ReminderAlert(
                user_id=current_user.id,
                title=title,
                message=message,
                category=category,
                alert_type="Scheduled"
            )
            db.session.add(alert)
            db.session.commit()
            flash("New crop reminder scheduled.", "success")
        return redirect(url_for("main.alerts"))
        
    alerts_list = ReminderAlert.query.filter_by(user_id=current_user.id).order_by(ReminderAlert.created_at.desc()).all()
    return render_template("alerts.html", alerts=alerts_list)

@main_bp.route("/alerts/<int:alert_id>/dismiss", methods=["POST"])
@login_required
def dismiss_alert(alert_id):
    alert = ReminderAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
    if alert:
        alert.is_read = True
        db.session.commit()
        flash("Alert marked as completed.", "info")
    return redirect(url_for("main.alerts"))
