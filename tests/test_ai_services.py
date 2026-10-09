import pytest
from services.disease_classifier import disease_classifier_service
from services.pest_classifier import pest_classifier_service
from services.crop_recommender import crop_recommender_service
from services.soil_service import soil_service
from services.irrigation_service import irrigation_service
from services.yield_service import yield_service
from services.risk_analysis import risk_analysis_service
from services.farming_agent import farming_agent_service
from services.rag_service import rag_service

def test_pest_classifier_honest_standby():
    res = pest_classifier_service.predict("fake_path.jpg")
    assert res["status"] == "not_configured"
    assert "dedicated" in res["error"].lower()
    species = pest_classifier_service.get_supported_species()
    assert len(species) == 5

def test_crop_recommender_service():
    res = crop_recommender_service.recommend(
        n=90, p=42, k=43, temperature=24.0, humidity=82.0, ph=6.5, rainfall=220.0
    )
    assert res["status"] == "success"
    assert "top_crop" in res
    assert len(res["recommendations"]) > 0

def test_crop_recommender_invalid_inputs():
    res = crop_recommender_service.recommend(
        n=-10, p=40, k=40, temperature=20, humidity=50, ph=6.5, rainfall=100
    )
    assert res["status"] == "error"
    assert "Nutrient values" in res["error"]

def test_soil_service_interpretation():
    res = soil_service.interpret_measurements(
        ph=5.2, nitrogen=180, phosphorus=8, potassium=95, target_crop="Tomato"
    )
    assert res["status"] == "success"
    assert len(res["deficiencies"]) >= 3
    assert any("acidity" in d.lower() for d in res["deficiencies"])

def test_irrigation_guidance():
    res = irrigation_service.calculate_guidance(
        crop_type="Tomato", growth_stage="Flowering", soil_type="Red Loam",
        moisture_input_mode="manual", soil_moisture_pct=25.0, temp_c=30.0, rain_forecast_mm=0.0
    )
    assert res["status"] == "success"
    assert res["crop_coefficient_kc"] == 1.15
    assert res["advisory_status"] == "Irrigate Promptly (High Deficit)"
    assert res["water_liters_per_sqm"] > 0

def test_risk_analysis_late_blight():
    res = risk_analysis_service.evaluate_risk(
        crop_type="Tomato", growth_stage="Vegetative",
        temperature_c=18.0, humidity_pct=88.0, rainfall_mm=5.0
    )
    assert res["status"] == "success"
    assert res["overall_severity"] == "High"
    assert any("Late Blight" in rf["hazard"] for rf in res["risk_factors"])

def test_farming_agent_tool_dispatch(app):
    with app.app_context():
        # Dispatch weather tool
        w_res = farming_agent_service.dispatch_tool("get_weather_information", 1, {"location": "Bengaluru"})
        assert w_res["status"] in ["success", "network_unavailable"]

        # Unauthorized tool rejection
        bad_tool = farming_agent_service.dispatch_tool("execute_shell_command", 1, {})
        assert bad_tool["status"] == "error"
        assert "Unauthorized" in bad_tool["message"]
