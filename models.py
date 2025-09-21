from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DailyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.Column(db.Text)
    tone = db.Column(db.String(50))
    audience = db.Column(db.String(50))
    format_type = db.Column(db.String(50))
    result = db.Column(db.Text)
