import json
from datetime import datetime
from models.database import db

class CropAnalysis(db.Model):
    __tablename__ = "crop_analyses"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    crop_type = db.Column(db.String(50), default="Tomato", nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
    predicted_class = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    alternative_predictions = db.Column(db.Text, default="[]") # JSON list of {class, confidence}
    heatmap_filename = db.Column(db.String(255), nullable=True)
    recommendations = db.Column(db.Text, nullable=True) # Practical agricultural guidelines
    scientific_citations = db.Column(db.Text, nullable=True) # ICAR / University publications
    model_version = db.Column(db.String(50), default="v1.0.0-mobilenetv2")
    is_preliminary = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_alternatives(self):
        try:
            return json.loads(self.alternative_predictions)
        except Exception:
            return []

class PestAnalysis(db.Model):
    __tablename__ = "pest_analyses"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    image_filename = db.Column(db.String(255), nullable=False)
    detected_pest = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    alternative_predictions = db.Column(db.Text, default="[]")
    organic_control = db.Column(db.Text, nullable=True)
    chemical_control = db.Column(db.Text, nullable=True)
    model_version = db.Column(db.String(50), default="v1.0.0-pest-detector")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_alternatives(self):
        try:
            return json.loads(self.alternative_predictions)
        except Exception:
            return []

class SoilRecord(db.Model):
    __tablename__ = "soil_records"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plot_id = db.Column(db.Integer, db.ForeignKey("crop_plots.id"), nullable=True)
    ph = db.Column(db.Float, nullable=False)
    nitrogen = db.Column(db.Float, nullable=False) # N (kg/ha or mg/kg)
    phosphorus = db.Column(db.Float, nullable=False) # P (kg/ha)
    potassium = db.Column(db.Float, nullable=False) # K (kg/ha)
    organic_carbon_pct = db.Column(db.Float, default=0.5)
    electrical_conductivity = db.Column(db.Float, default=0.4) # dS/m
    status_summary = db.Column(db.String(255), nullable=True)
    deficiency_tags = db.Column(db.String(255), nullable=True)
    expert_advice = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class IrrigationRecord(db.Model):
    __tablename__ = "irrigation_records"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plot_id = db.Column(db.Integer, db.ForeignKey("crop_plots.id"), nullable=True)
    soil_moisture_pct = db.Column(db.Float, nullable=True)
    soil_type = db.Column(db.String(50), default="Loam")
    crop_stage = db.Column(db.String(50), default="Vegetative")
    temperature_c = db.Column(db.Float, nullable=True)
    rain_probability_pct = db.Column(db.Float, nullable=True)
    water_recommended_liters_per_sqm = db.Column(db.Float, nullable=True)
    advisory_status = db.Column(db.String(50), default="Sufficient") # Skip, Irrigate Light, Irrigate Heavy
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class YieldRecord(db.Model):
    __tablename__ = "yield_records"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    crop_type = db.Column(db.String(50), nullable=False)
    acreage = db.Column(db.Float, nullable=False)
    season = db.Column(db.String(50), default="Kharif") # Kharif, Rabi, Zaid
    predicted_yield_quintals = db.Column(db.Float, nullable=False)
    yield_lower_bound = db.Column(db.Float, nullable=False)
    yield_upper_bound = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(50), default="v1.0.0-randomforest")
    evaluation_mae = db.Column(db.Float, default=1.85)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MarketPriceRecord(db.Model):
    __tablename__ = "market_price_records"
    
    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String(60), nullable=False, index=True)
    market_mandi = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(60), default="Karnataka")
    min_price_rs = db.Column(db.Float, nullable=False)
    max_price_rs = db.Column(db.Float, nullable=False)
    modal_price_rs = db.Column(db.Float, nullable=False) # per Quintal
    arrival_date = db.Column(db.Date, default=datetime.utcnow)
    source_name = db.Column(db.String(100), default="e-NAM / Karnataka APMC Agricultural Marketing Board")
    
    def __repr__(self):
        return f"<MarketPrice {self.commodity} @ {self.market_mandi}: ₹{self.modal_price_rs}/Q>"

class ModelRegistryEntry(db.Model):
    __tablename__ = "model_registry"
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False, unique=True)
    version = db.Column(db.String(50), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)
    task = db.Column(db.String(50), default="Classification") # Classification, Pest, Yield, CropRecommendation
    supported_classes = db.Column(db.Text, nullable=False) # JSON list
    framework = db.Column(db.String(50), default="Scikit-Learn/PyTorch")
    dataset_name = db.Column(db.String(100), default="PlantVillage")
    test_accuracy = db.Column(db.Float, nullable=True)
    confusion_matrix_json = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="Active") # Active, Deprecated, Standby
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
