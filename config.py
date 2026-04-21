"""
Configuration file for TR Manila Workstation Reservation System
"""
import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tr_manila_workstation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Microsoft 365 Configuration
    CLIENT_ID = os.environ.get('M365_CLIENT_ID', '')
    CLIENT_SECRET = os.environ.get('M365_CLIENT_SECRET', '')
    TENANT_ID = os.environ.get('M365_TENANT_ID', '')
    AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('M365_TENANT_ID', 'common')}"
    SCOPE = ['https://graph.microsoft.com/.default']
    
    # Outlook Calendar Integration
    OUTLOOK_ENABLED = os.environ.get('OUTLOOK_ENABLED', 'False').lower() == 'true'
    
    # Floor Plan Configuration - TR Manila
    FLOOR_PLANS = {
        '9F': {
            'name': '9th Floor',
            'zones': [
                {'name': 'CS&S', 'start': 1, 'end': 120, 'color': '#4CAF50'},
                {'name': 'C2C', 'start': 121, 'end': 160, 'color': '#2196F3'},
                {'name': 'Ops Enablement', 'start': 161, 'end': 186, 'color': '#FF9800'},
                {'name': 'CS&S (from 10F)', 'start': 187, 'end': 214, 'color': '#9C27B0'}
            ],
            'total_seats': 214
        },
        '10F': {
            'name': '10th Floor',
            'zones': [
                {'name': 'Content Ops + FindLaw', 'start': 1, 'end': 15, 'color': '#F44336'},
                {'name': 'Content Ops + BDR', 'start': 16, 'end': 60, 'color': '#E91E63'},
                {'name': 'Content Ops', 'start': 71, 'end': 105, 'color': '#9C27B0'},
                {'name': 'Product Delivery + AEM, Reuters Tech, Comm Ex', 'start': 106, 'end': 140, 'color': '#673AB7'},
                {'name': 'Commentary (Content)', 'start': 141, 'end': 142, 'color': '#3F51B5'},
                {'name': 'Product Content', 'start': 143, 'end': 146, 'color': '#2196F3'},
                {'name': 'Editorial', 'start': 147, 'end': 180, 'color': '#03A9F4'},
                {'name': 'Editorial / PD Online', 'start': 181, 'end': 193, 'color': '#00BCD4'}
            ],
            'total_seats': 223
        }
    }
    
    # Time Slots
    TIME_SLOTS = [
        {'id': 'full_day', 'name': 'Full Day (8:00 AM - 5:00 PM)', 'start': '08:00', 'end': '17:00'},
        {'id': 'morning', 'name': 'Morning (8:00 AM - 12:00 PM)', 'start': '08:00', 'end': '12:00'},
        {'id': 'afternoon', 'name': 'Afternoon (1:00 PM - 5:00 PM)', 'start': '13:00', 'end': '17:00'}
    ]
    
    # Booking Rules
    MAX_ADVANCE_BOOKING_DAYS = 14  # Can book up to 2 weeks in advance
    
    # RTO Compliance
    RTO_MULTIPLIER = 5  # Formula: (In-Office Days / Available Days) × 5
    
    # Exemption Types
    EXEMPTION_TYPES = [
        'Approved Time Off',
        'Work-From-Anywhere Request',
        'Company Holiday',
        'Site Exception'
    ]