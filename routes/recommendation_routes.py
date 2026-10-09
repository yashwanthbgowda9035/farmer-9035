from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from services.crop_recommender import crop_recommender_service
from services.weather_service import weather_service

recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/recommendations")

@recommendation_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    result = None
    weather = weather_service.get_weather()
    default_temp = weather.get("temperature_c", 25.0) if weather.get("status") == "success" else 25.0
    default_hum = weather.get("humidity_pct", 65.0) if weather.get("status") == "success" else 65.0
    
    if request.method == "POST":
        try:
            n = float(request.form.get("nitrogen", 90))
            p = float(request.form.get("phosphorus", 42))
            k = float(request.form.get("potassium", 43))
            temp = float(request.form.get("temperature", default_temp))
            humidity = float(request.form.get("humidity", default_hum))
            ph = float(request.form.get("ph", 6.5))
            rainfall = float(request.form.get("rainfall", 200))
            
            result = crop_recommender_service.recommend(n, p, k, temp, humidity, ph, rainfall)
            if result.get("status") == "error":
                flash(result["error"], "danger")
                result = None
        except ValueError:
            flash("Please enter valid numerical parameters.", "danger")
            
    is_configured = crop_recommender_service.is_configured()
    return render_template(
        "recommendations.html",
        result=result,
        default_temp=default_temp,
        default_hum=default_hum,
        is_configured=is_configured
    )
