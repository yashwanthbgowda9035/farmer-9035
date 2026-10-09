from datetime import datetime
from models.database import db

class ReminderAlert(db.Model):
    __tablename__ = "reminder_alerts"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="Observation") # Disease, Weather, Irrigation, Observation, Market
    alert_type = db.Column(db.String(30), default="Scheduled") # Scheduled, AI-Risk-Alert, System
    is_read = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ReminderAlert '{self.title}' (user={self.user_id})>"
