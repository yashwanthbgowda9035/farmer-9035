from datetime import datetime
from models.database import db

class CropPlot(db.Model):
    __tablename__ = "crop_plots"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plot_name = db.Column(db.String(100), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False) # e.g. Tomato, Potato, Rice, Maize
    variety = db.Column(db.String(50), default="Standard")
    acreage = db.Column(db.Float, default=1.0)
    sowing_date = db.Column(db.Date, nullable=True)
    soil_type = db.Column(db.String(50), default="Red Loam") # Red Loam, Black Soil, Alluvial
    irrigation_system = db.Column(db.String(50), default="Drip") # Drip, Sprinkler, Flood, Rainfed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    observations = db.relationship("CropObservation", backref="plot", lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CropPlot {self.plot_name}: {self.crop_type}>"

class CropObservation(db.Model):
    __tablename__ = "crop_observations"
    
    id = db.Column(db.Integer, primary_key=True)
    plot_id = db.Column(db.Integer, db.ForeignKey("crop_plots.id"), nullable=False, index=True)
    observation_date = db.Column(db.Date, default=datetime.utcnow)
    growth_stage = db.Column(db.String(50), default="Vegetative") # Seedling, Vegetative, Flowering, Fruiting, Harvesting
    plant_height_cm = db.Column(db.Float, nullable=True)
    estimated_leaf_area_index = db.Column(db.Float, nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Observation Plot={self.plot_id} Stage={self.growth_stage} Date={self.observation_date}>"
