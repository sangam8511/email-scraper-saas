from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    accounts = db.relationship('EmailAccount', backref='owner', lazy=True)
    campaigns = db.relationship('Campaign', backref='owner', lazy=True)

class EmailAccount(db.Model):
    __tablename__ = 'email_accounts'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    email = db.Column(db.String(120), nullable=False)
    app_password = db.Column(db.String(256), nullable=False)
    sender_name = db.Column(db.String(120), nullable=True)
    daily_limit = db.Column(db.Integer, default=150)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    niche = db.Column(db.String(120), nullable=True)
    subject = db.Column(db.String(256), nullable=True)
    plain_text = db.Column(db.Text, nullable=True)
    template_html = db.Column(db.Text, nullable=True)
    is_running = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    leads = db.relationship('Lead', backref='campaign', lazy=True)

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    
    name_full = db.Column(db.String(256), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(256), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    sent_at = db.Column(db.DateTime, nullable=True)
    bounced = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
