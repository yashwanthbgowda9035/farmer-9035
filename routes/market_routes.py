from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from services.market_service import market_service
from services.yield_service import yield_service

market_bp = Blueprint("market", __name__, url_prefix="/market")

@market_bp.route("/", methods=["GET"])
@login_required
def index():
    commodity = request.args.get("commodity", "Tomato")
    mandi = request.args.get("mandi", "Kolar APMC")
    market_data = market_service.get_market_trends(commodity, mandi)
    return render_template("market.html", market_data=market_data, selected_commodity=commodity, selected_mandi=mandi)

@market_bp.route("/yield", methods=["GET", "POST"])
@login_required
def yield_estimator():
    result = None
    is_configured = yield_service.is_configured()
    
    if request.method == "POST":
        crop = request.form.get("crop", "Tomato")
        try:
            acreage = float(request.form.get("acreage", 1.0))
            rainfall = float(request.form.get("rainfall_mm", 750.0))
            fertilizer = float(request.form.get("fertilizer_kg_ha", 120.0))
            ph = float(request.form.get("soil_ph", 6.5))
            irrigation = request.form.get("irrigation", "Drip")
            
            result = yield_service.estimate_yield(
                crop=crop,
                acreage=acreage,
                rainfall_mm=rainfall,
                fertilizer_kg_ha=fertilizer,
                soil_ph=ph,
                irrigation=irrigation
            )
        except ValueError:
            flash("Invalid input values provided for yield regression.", "danger")
            
    return render_template("yield.html", result=result, is_configured=is_configured)
