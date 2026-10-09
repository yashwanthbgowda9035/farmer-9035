from flask import Blueprint, render_template, request
from flask_login import login_required
from services.weather_service import weather_service
from services.risk_analysis import risk_analysis_service

weather_bp = Blueprint("weather", __name__, url_prefix="/weather")

@weather_bp.route("/")
@login_required
def index():
    crop = request.args.get("crop", "Tomato")
    stage = request.args.get("stage", "Vegetative")
    
    weather_data = weather_service.get_weather()
    risk_assessment = None
    
    if weather_data.get("status") == "success":
        risk_assessment = risk_analysis_service.evaluate_risk(
            crop_type=crop,
            growth_stage=stage,
            temperature_c=weather_data["temperature_c"],
            humidity_pct=weather_data["humidity_pct"],
            rainfall_mm=weather_data["rainfall_mm"],
            rain_forecast_prob=weather_data["forecast"][0]["rain_prob"] if weather_data.get("forecast") else 20
        )
        
    return render_template(
        "weather.html",
        weather=weather_data,
        risk_assessment=risk_assessment,
        selected_crop=crop,
        selected_stage=stage
    )
