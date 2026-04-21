"""
Main Flask application for TR Manila Workstation Reservation System
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from datetime import datetime, date, timedelta
import calendar
import holidays

from models import db, User, Desk, Reservation, Exemption, Holiday, RTOCompliance, Admin
from config import Config
from outlook_integration import OutlookCalendar

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Outlook integration
outlook = OutlookCalendar(app.config)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def init_database():
    """Initialize database with desks and Philippine holidays"""
    with app.app_context():
        db.create_all()
        
        # Initialize desks if not exists
        if Desk.query.count() == 0:
            init_desks()
        
        # Initialize Philippine holidays if not exists
        if Holiday.query.filter_by(holiday_type='philippine').count() == 0:
            init_philippine_holidays()
        
        # Create default admin if not exists
        if User.query.filter_by(email='admin@tr-manila.com').first() is None:
            admin = User(
                email='admin@tr-manila.com',
                username='admin',
                full_name='System Administrator',
                role='admin'
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            
            # Add to admin list
            admin_record = Admin(user_id=admin.id)
            db.session.add(admin_record)
            db.session.commit()


def init_desks():
    """Initialize all desks based on floor plan configuration"""
    for floor, floor_data in Config.FLOOR_PLANS.items():
        for zone in floor_data['zones']:
            for desk_num in range(zone['start'], zone['end'] + 1):
                desk_number = f"{floor}-{desk_num:03d}"
                desk = Desk(
                    desk_number=desk_number,
                    floor=floor,
                    zone=zone['name'],
                    status='available'
                )
                db.session.add(desk)
    db.session.commit()
    print(f"Initialized {Desk.query.count()} desks")


def init_philippine_holidays():
    """Initialize Philippine holidays for current and next year"""
    ph_holidays = holidays.Philippines()
    current_year = datetime.now().year
    
    for year in [current_year, current_year + 1]:
        for holiday_date, holiday_name in sorted(ph_holidays.items()):
            if holiday_date.year == year:
                holiday = Holiday(
                    holiday_date=holiday_date,
                    holiday_name=holiday_name,
                    holiday_type='philippine',
                    is_working_day=False
                )
                db.session.add(holiday)
    db.session.commit()
    print(f"Initialized {Holiday.query.filter_by(holiday_type='philippine').count()} Philippine holidays")


# ============ ROUTES ============

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        flash('Invalid email or password', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email')
        username = data.get('username')
        full_name = data.get('full_name')
        password = data.get('password')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email already registered'}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(email=email, username=username, full_name=full_name, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('login')})
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', user=current_user)


@app.route('/floor-map')
@login_required
def floor_map():
    """Interactive floor map page"""
    return render_template('floor_map.html', 
                         floor_plans=Config.FLOOR_PLANS,
                         time_slots=Config.TIME_SLOTS)


@app.route('/admin-panel')
@login_required
def admin_panel():
    """Admin panel page - only accessible to admins"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('admin_panel.html')


@app.route('/api/desks', methods=['GET'])
@login_required
def get_desks():
    """Get all desks with optional filters"""
    floor = request.args.get('floor')
    date_str = request.args.get('date')
    time_slot = request.args.get('time_slot')
    
    query = Desk.query.filter_by(is_active=True, status='available')
    
    if floor:
        query = query.filter_by(floor=floor)
    
    desks = query.all()
    
    # If date and time_slot provided, check availability
    if date_str and time_slot:
        reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        reservations = Reservation.query.filter_by(
            reservation_date=reservation_date,
            time_slot=time_slot,
            status='confirmed'
        ).all()
        
        # Create a map of desk_id to reservation details
        reservation_map = {r.desk_id: r for r in reservations}
        
        desks_data = []
        for desk in desks:
            desk_info = {
                'id': desk.id,
                'desk_number': desk.desk_number,
                'floor': desk.floor,
                'zone': desk.zone,
                'status': desk.status,
                'is_available': desk.id not in reservation_map
            }
            
            # If desk is reserved, include user info
            if desk.id in reservation_map:
                reservation = reservation_map[desk.id]
                desk_info['reserved_by'] = reservation.user.full_name
                desk_info['reserved_by_email'] = reservation.user.email
            
            desks_data.append(desk_info)
    else:
        desks_data = [{
            'id': desk.id,
            'desk_number': desk.desk_number,
            'floor': desk.floor,
            'zone': desk.zone,
            'status': desk.status
        } for desk in desks]
    
    return jsonify(desks_data)


@app.route('/api/reservations', methods=['GET'])
@login_required
def get_reservations():
    """Get reservations with optional filters"""
    date_str = request.args.get('date')
    floor = request.args.get('floor')
    user_only = request.args.get('user_only', 'false').lower() == 'true'
    
    query = Reservation.query.filter_by(status='confirmed')
    
    if user_only:
        query = query.filter_by(user_id=current_user.id)
    
    if date_str:
        reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        query = query.filter_by(reservation_date=reservation_date)
    
    if floor:
        desk_ids = [d.id for d in Desk.query.filter_by(floor=floor).all()]
        query = query.filter(Reservation.desk_id.in_(desk_ids))
    
    reservations = query.order_by(Reservation.reservation_date.desc()).all()
    
    return jsonify([{
        'id': r.id,
        'desk_number': r.desk.desk_number,
        'floor': r.desk.floor,
        'zone': r.desk.zone,
        'user_name': r.user.full_name,
        'user_email': r.user.email,
        'reservation_date': r.reservation_date.strftime('%Y-%m-%d'),
        'time_slot': r.time_slot,
        'start_time': r.start_time.strftime('%H:%M'),
        'end_time': r.end_time.strftime('%H:%M'),
        'status': r.status
    } for r in reservations])


@app.route('/api/reserve', methods=['POST'])
@login_required
def create_reservation():
    """Create a new reservation"""
    data = request.get_json()
    
    desk_id = data.get('desk_id')
    date_str = data.get('date')
    time_slot_id = data.get('time_slot')
    
    # Validate inputs
    if not all([desk_id, date_str, time_slot_id]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Parse date
    try:
        reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400
    
    # Check if date is in the past
    if reservation_date < date.today():
        return jsonify({'success': False, 'message': 'Cannot book for past dates'}), 400
    
    # Check advance booking limit
    max_date = date.today() + timedelta(days=Config.MAX_ADVANCE_BOOKING_DAYS)
    if reservation_date > max_date:
        return jsonify({'success': False, 'message': f'Can only book up to {Config.MAX_ADVANCE_BOOKING_DAYS} days in advance'}), 400
    
    # Check if it's a holiday
    holiday = Holiday.query.filter_by(holiday_date=reservation_date, is_working_day=False).first()
    if holiday:
        return jsonify({'success': False, 'message': f'Cannot book on {holiday.holiday_name}'}), 400
    
    # Get time slot details
    time_slot = next((ts for ts in Config.TIME_SLOTS if ts['id'] == time_slot_id), None)
    if not time_slot:
        return jsonify({'success': False, 'message': 'Invalid time slot'}), 400
    
    # Check if desk exists and is available
    desk = Desk.query.get(desk_id)
    if not desk or not desk.is_active or desk.status != 'available':
        return jsonify({'success': False, 'message': 'Desk not available'}), 400
    
    # Check if desk is already booked for this date and time slot
    existing = Reservation.query.filter_by(
        desk_id=desk_id,
        reservation_date=reservation_date,
        time_slot=time_slot_id,
        status='confirmed'
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Desk already booked for this time slot'}), 400
    
    # Create reservation
    start_time = datetime.strptime(time_slot['start'], '%H:%M').time()
    end_time = datetime.strptime(time_slot['end'], '%H:%M').time()
    
    reservation = Reservation(
        user_id=current_user.id,
        desk_id=desk_id,
        reservation_date=reservation_date,
        time_slot=time_slot_id,
        start_time=start_time,
        end_time=end_time,
        status='confirmed'
    )
    
    db.session.add(reservation)
    db.session.commit()
    
    # Try to create Outlook calendar event if enabled
    if Config.OUTLOOK_ENABLED:
        try:
            event_id = outlook.create_calendar_event(
                user_email=current_user.email,
                subject=f"Workstation Booking - {desk.desk_number}",
                start_datetime=datetime.combine(reservation_date, start_time),
                end_datetime=datetime.combine(reservation_date, end_time),
                location=f"{desk.floor} - {desk.zone}",
                body=f"Workstation: {desk.desk_number}\nFloor: {desk.floor}\nZone: {desk.zone}"
            )
            if event_id:
                reservation.outlook_event_id = event_id
                db.session.commit()
        except Exception as e:
            print(f"Failed to create Outlook event: {str(e)}")
    
    return jsonify({
        'success': True,
        'message': 'Reservation created successfully',
        'reservation_id': reservation.id
    })


@app.route('/api/reserve/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    """Cancel a reservation"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Check permissions
    if reservation.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Cancel the reservation
    reservation.status = 'cancelled'
    reservation.cancelled_at = datetime.utcnow()
    reservation.cancelled_by = current_user.id
    
    db.session.commit()
    
    # Cancel Outlook event if exists
    if reservation.outlook_event_id and Config.OUTLOOK_ENABLED:
        try:
            outlook.delete_calendar_event(current_user.email, reservation.outlook_event_id)
        except Exception as e:
            print(f"Failed to delete Outlook event: {str(e)}")
    
    return jsonify({'success': True, 'message': 'Reservation cancelled successfully'})


@app.route('/api/rto-compliance')
@login_required
def get_rto_compliance():
    """Get RTO compliance for current user"""
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    compliance = calculate_rto_compliance(current_user.id, month, year)
    
    return jsonify(compliance)


def calculate_rto_compliance(user_id, month, year):
    """Calculate RTO compliance for a user for a specific month"""
    # Get first and last day of month
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    # Count weekdays in the month
    total_weekdays = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            total_weekdays += 1
        current_date += timedelta(days=1)
    
    # Get holidays in this month
    holidays_count = Holiday.query.filter(
        Holiday.holiday_date >= start_date,
        Holiday.holiday_date <= end_date,
        Holiday.is_working_day == False
    ).count()
    
    # Get exemptions for this user in this month
    exemptions_count = Exemption.query.filter(
        Exemption.user_id == user_id,
        Exemption.exemption_date >= start_date,
        Exemption.exemption_date <= end_date,
        Exemption.is_approved == True
    ).count()
    
    # Calculate available days (total weekdays - holidays - exemptions)
    available_days = total_weekdays - holidays_count - exemptions_count
    
    # Count in-office days (days with confirmed reservations)
    in_office_days = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.reservation_date >= start_date,
        Reservation.reservation_date <= end_date,
        Reservation.status == 'confirmed'
    ).distinct(Reservation.reservation_date).count()
    
    # Calculate compliance percentage
    if available_days > 0:
        compliance_percentage = (in_office_days / available_days) * Config.RTO_MULTIPLIER
    else:
        compliance_percentage = 0.0
    
    # Update or create RTO compliance record
    rto_record = RTOCompliance.query.filter_by(
        user_id=user_id,
        month=month,
        year=year
    ).first()
    
    if rto_record:
        rto_record.in_office_days = in_office_days
        rto_record.available_days = available_days
        rto_record.exemption_days = exemptions_count
        rto_record.compliance_percentage = compliance_percentage
        rto_record.calculated_at = datetime.utcnow()
    else:
        rto_record = RTOCompliance(
            user_id=user_id,
            month=month,
            year=year,
            in_office_days=in_office_days,
            available_days=available_days,
            exemption_days=exemptions_count,
            compliance_percentage=compliance_percentage
        )
        db.session.add(rto_record)
    
    db.session.commit()
    
    return {
        'month': month,
        'year': year,
        'in_office_days': in_office_days,
        'available_days': available_days,
        'exemption_days': exemptions_count,
        'holidays': holidays_count,
        'total_weekdays': total_weekdays,
        'compliance_percentage': round(compliance_percentage, 2)
    }


@app.route('/api/exemptions', methods=['GET', 'POST'])
@login_required
def manage_exemptions():
    """Get or create exemptions"""
    if request.method == 'GET':
        exemptions = Exemption.query.filter_by(user_id=current_user.id).order_by(Exemption.exemption_date.desc()).all()
        return jsonify([{
            'id': e.id,
            'exemption_date': e.exemption_date.strftime('%Y-%m-%d'),
            'exemption_type': e.exemption_type,
            'reason': e.reason,
            'is_approved': e.is_approved
        } for e in exemptions])
    
    # POST - Create new exemption
    data = request.get_json()
    exemption_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    exemption_type = data.get('type')
    reason = data.get('reason', '')
    
    if exemption_type not in Config.EXEMPTION_TYPES:
        return jsonify({'success': False, 'message': 'Invalid exemption type'}), 400
    
    # Check if exemption already exists
    existing = Exemption.query.filter_by(
        user_id=current_user.id,
        exemption_date=exemption_date
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Exemption already exists for this date'}), 400
    
    exemption = Exemption(
        user_id=current_user.id,
        exemption_date=exemption_date,
        exemption_type=exemption_type,
        reason=reason,
        is_approved=True,
        created_by=current_user.id
    )
    
    db.session.add(exemption)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Exemption added successfully'})


@app.route('/api/holidays')
@login_required
def get_holidays():
    """Get all holidays"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    holidays_list = Holiday.query.filter(
        db.extract('year', Holiday.holiday_date) == year
    ).order_by(Holiday.holiday_date).all()
    
    return jsonify([{
        'id': h.id,
        'date': h.holiday_date.strftime('%Y-%m-%d'),
        'name': h.holiday_name,
        'type': h.holiday_type,
        'is_working_day': h.is_working_day
    } for h in holidays_list])


# Admin routes
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    """Admin - manage users"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([{
            'id': u.id,
            'email': u.email,
            'username': u.username,
            'full_name': u.full_name,
            'role': u.role,
            'is_active': u.is_active
        } for u in users])
    
    # POST - Create new user or admin
    data = request.get_json()
    action = data.get('action')
    
    if action == 'create':
        email = data.get('email')
        username = data.get('username')
        full_name = data.get('full_name')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        user = User(email=email, username=username, full_name=full_name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # If admin, add to admin list
        if role == 'admin':
            admin_record = Admin(user_id=user.id, granted_by=current_user.id)
            db.session.add(admin_record)
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'User created successfully'})
    
    elif action == 'promote':
        user_id = data.get('user_id')
        user = User.query.get_or_404(user_id)
        user.role = 'admin'
        db.session.commit()
        
        # Add to admin list if not exists
        if not Admin.query.filter_by(user_id=user_id).first():
            admin_record = Admin(user_id=user_id, granted_by=current_user.id)
            db.session.add(admin_record)
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'User promoted to admin'})
    
    return jsonify({'success': False, 'message': 'Invalid action'}), 400


if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)