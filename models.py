"""
Database models for TR Manila Workstation Reservation System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic', foreign_keys='Reservation.user_id')
    exemptions = db.relationship('Exemption', backref='user', lazy='dynamic', foreign_keys='Exemption.user_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.email}>'


class Desk(db.Model):
    """Desk/Workstation model"""
    __tablename__ = 'desks'
    
    id = db.Column(db.Integer, primary_key=True)
    desk_number = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g., "9F-001", "10F-105"
    floor = db.Column(db.String(10), nullable=False, index=True)  # "9F" or "10F"
    zone = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='available', nullable=False)  # 'available', 'unavailable', 'maintenance'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='desk', lazy='dynamic')
    
    def __repr__(self):
        return f'<Desk {self.desk_number}>'


class Reservation(db.Model):
    """Reservation model for desk bookings"""
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    desk_id = db.Column(db.Integer, db.ForeignKey('desks.id'), nullable=False, index=True)
    reservation_date = db.Column(db.Date, nullable=False, index=True)
    time_slot = db.Column(db.String(50), nullable=False)  # 'full_day', 'morning', 'afternoon'
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='confirmed', nullable=False)  # 'confirmed', 'cancelled', 'completed'
    outlook_event_id = db.Column(db.String(255), nullable=True)  # For Outlook integration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<Reservation {self.id}: Desk {self.desk_id} on {self.reservation_date}>'


class Exemption(db.Model):
    """Exemption days model for RTO compliance calculation"""
    __tablename__ = 'exemptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    exemption_date = db.Column(db.Date, nullable=False, index=True)
    exemption_type = db.Column(db.String(100), nullable=False)  # From EXEMPTION_TYPES in config
    reason = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<Exemption {self.id}: User {self.user_id} on {self.exemption_date}>'


class Holiday(db.Model):
    """Holiday model for Philippine holidays and company holidays"""
    __tablename__ = 'holidays'
    
    id = db.Column(db.Integer, primary_key=True)
    holiday_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    holiday_name = db.Column(db.String(150), nullable=False)
    holiday_type = db.Column(db.String(50), nullable=False)  # 'philippine', 'company'
    is_working_day = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Holiday {self.holiday_name} on {self.holiday_date}>'


class RTOCompliance(db.Model):
    """RTO Compliance tracking model"""
    __tablename__ = 'rto_compliance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    in_office_days = db.Column(db.Integer, default=0, nullable=False)
    available_days = db.Column(db.Integer, default=0, nullable=False)
    exemption_days = db.Column(db.Integer, default=0, nullable=False)
    compliance_percentage = db.Column(db.Float, default=0.0, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='rto_records')
    
    # Unique constraint for user per month/year
    __table_args__ = (db.UniqueConstraint('user_id', 'month', 'year', name='_user_month_year_uc'),)
    
    def __repr__(self):
        return f'<RTOCompliance User {self.user_id}: {self.month}/{self.year} - {self.compliance_percentage}%>'


class Admin(db.Model):
    """Admin list model - separate table to track admin access"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='admin_record')
    granter = db.relationship('User', foreign_keys=[granted_by])
    
    def __repr__(self):
        return f'<Admin {self.user_id}>'