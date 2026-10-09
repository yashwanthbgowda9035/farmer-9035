from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from models.crop import CropPlot
from services.irrigation_service import irrigation_service
from services.weather_service import weather_service
from services.rag_service import rag_service

irrigation_bp = Blueprint("irrigation", __name__, url_prefix="/irrigation")

@irrigation_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    guidance = None
    plots = CropPlot.query.filter_by(user_id=current_user.id).all()
    weather = weather_service.get_weather()
    
    current_temp = weather.get("temperature_c", 27.0) if weather.get("status") == "success" else 27.0
    rain_forecast = weather.get("rainfall_mm", 0.0) if weather.get("status") == "success" else 0.0
    
    if request.method == "POST":
        crop_type = request.form.get("crop_type", "Tomato")
        growth_stage = request.form.get("growth_stage", "Vegetative")
        soil_type = request.form.get("soil_type", "Red Loam")
        mode = request.form.get("moisture_input_mode", "manual")
        
        try:
            moisture = request.form.get("soil_moisture_pct")
            moisture_val = float(moisture) if moisture else None
            
            guidance = irrigation_service.calculate_guidance(
                crop_type=crop_type,
                growth_stage=growth_stage,
                soil_type=soil_type,
                moisture_input_mode=mode,
                soil_moisture_pct=moisture_val,
                temp_c=current_temp,
                rain_forecast_mm=rain_forecast
            )
        except ValueError:
            flash("Invalid input values provided.", "danger")
            
    return render_template(
        "irrigation.html",
        guidance=guidance,
        plots=plots,
        weather=weather,
        current_temp=current_temp,
        rain_forecast=rain_forecast
    )

@irrigation_bp.route("/fertilizer", methods=["GET", "POST"])
@login_required
def fertilizer():
    advisory = None
    crop = request.args.get("crop", "Tomato")
    stage = request.args.get("stage", "Vegetative")
    
    if request.method == "POST":
        crop = request.form.get("crop", "Tomato")
        stage = request.form.get("stage", "Vegetative")
        
    # Search RAG knowledge base for certified ICAR fertilizer recommendations
    rag_query = f"Recommended fertilizer dose NPK application for {crop} at {stage} stage"
    rag_result = rag_service.query(rag_query)
    
    return render_template(
        "fertilizer.html",
        crop=crop,
        stage=stage,
        rag_result=rag_result
    )
