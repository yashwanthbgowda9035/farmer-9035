from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="farmer", nullable=False) # 'farmer' or 'admin'
    preferred_language = db.Column(db.String(10), default="en", nullable=False) # 'en' or 'kn'
    state_district = db.Column(db.String(100), default="Bengaluru, Karnataka")
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    plots = db.relationship("CropPlot", backref="farmer", lazy=True, cascade="all, delete-orphan")
    analyses = db.relationship("CropAnalysis", backref="farmer", lazy=True, cascade="all, delete-orphan")
    pest_analyses = db.relationship("PestAnalysis", backref="farmer", lazy=True, cascade="all, delete-orphan")
    soil_records = db.relationship("SoilRecord", backref="farmer", lazy=True, cascade="all, delete-orphan")
    reminders = db.relationship("ReminderAlert", backref="farmer", lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
