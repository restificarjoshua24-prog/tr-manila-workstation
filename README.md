# TR Manila Workstation Reservation System

A comprehensive web-based office workstation reservation system with automated Return-to-Office (RTO) compliance tracking and Microsoft 365 integration.

## Features

### Core Functionality
- ✅ **Interactive Floor Maps**: Visual representation of 9th and 10th floor workstations (437 total seats)
- ✅ **Real-time Seat Availability**: Check available workstations by date and time slot
- ✅ **Workstation Booking**: Reserve desks up to 2 weeks in advance
- ✅ **Flexible Time Slots**: Full day, morning, or afternoon bookings
- ✅ **Booking Management**: Users can cancel their own bookings; admins can cancel any booking
- ✅ **RTO Compliance Dashboard**: Automated monthly compliance tracking with formula: (In-Office Days ÷ Available Days) × 5
- ✅ **Exemption Management**: Track time offs, work-from-anywhere, holidays, and site exceptions
- ✅ **Philippine Holidays**: Automatically populated and excluded from RTO calculations

### Microsoft 365 Integration
- ✅ **Outlook Calendar Sync**: Confirmed bookings automatically appear in user's Outlook calendar
- ✅ **Email Reminders**: 1-hour advance notifications for workstation reservations
- ✅ **Microsoft Graph API**: Seamless integration with Microsoft 365 ecosystem

### Access Control
- ✅ **User Role**: Book seats, view availability, cancel own bookings, track personal RTO
- ✅ **Admin Role**: View all bookings, cancel any booking, manage users, add admins

### Technical Features
- ✅ **Web & Mobile Responsive**: Accessible from desktop and mobile devices
- ✅ **RESTful API**: Clean API endpoints for all operations
- ✅ **SQLite Database**: Lightweight, serverless database (easily upgradeable to PostgreSQL)
- ✅ **Modern UI**: Bootstrap 5 with custom styling
- ✅ **Secure Authentication**: Password hashing and session management

## Technology Stack

- **Backend**: Python 3.8+, Flask 3.0
- **Database**: SQLite (production can use PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **Microsoft Integration**: MSAL, Microsoft Graph API
- **Holidays**: Python `holidays` library for Philippine holidays

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Microsoft 365 account (for Outlook integration - optional)

### Step 1: Clone or Download
```bash
cd Desktop
cd tr-manila-workstation-app
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

**Activate virtual environment:**
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///tr_manila_workstation.db

# Microsoft 365 Integration (Optional)
M365_CLIENT_ID=your-azure-app-client-id
M365_CLIENT_SECRET=your-azure-app-client-secret
M365_TENANT_ID=your-azure-tenant-id
OUTLOOK_ENABLED=False

# Set to True to enable Outlook integration
# OUTLOOK_ENABLED=True
```

### Step 5: Initialize Database
```bash
python app.py
```

This will:
- Create the database with all tables
- Initialize 437 workstations (9F: 214 seats, 10F: 223 seats)
- Populate Philippine holidays for 2026-2027
- Create default admin account

### Step 6: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

**Default Admin Credentials:**
- Email: `admin@tr-manila.com`
- Password: `Admin@123`

**Important**: Change the default admin password after first login!

## Microsoft 365 Integration Setup (Optional)

To enable Outlook calendar integration:

### 1. Register Application in Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Enter application name: "TR Manila Workstation System"
5. Select supported account types
6. Click **Register**

### 2. Configure API Permissions
1. Go to **API permissions**
2. Add **Microsoft Graph** permissions:
   - `Calendars.ReadWrite`
   - `User.Read.All`
3. Grant admin consent

### 3. Create Client Secret
1. Go to **Certificates & secrets**
2. Create new client secret
3. Copy the secret value (shown only once)

### 4. Update .env File
```env
M365_CLIENT_ID=<your-application-client-id>
M365_CLIENT_SECRET=<your-client-secret>
M365_TENANT_ID=<your-tenant-id>
OUTLOOK_ENABLED=True
```

### 5. Restart Application
```bash
python app.py
```

## Usage Guide

### For Users

#### 1. Register Account
- Navigate to login page
- Click "Register here"
- Fill in your details with corporate email
- Login with credentials

#### 2. Book a Workstation
- Go to **Floor Map**
- Select date and time slot
- Click **Check Availability**
- Click on a green (available) seat
- Review selection and click **Confirm Booking**
- Booking will appear in Outlook calendar (if enabled)

#### 3. View Reservations
- Go to **Dashboard**
- View **My Upcoming Reservations**
- Cancel bookings if needed

#### 4. Track RTO Compliance
- Dashboard shows current month compliance
- Formula: (In-Office Days ÷ Available Days) × 5
- Target: 5/5 (100% compliance)

#### 5. Add Exemption Days
- Click **Exemptions** on dashboard
- Select date and exemption type
- These days are excluded from RTO calculation

### For Admins

#### 1. View All Bookings
- Access **Floor Map**
- View all current reservations
- Filter by floor and date

#### 2. Cancel Any Booking
- Admin can cancel any user's booking
- Useful for emergencies or conflicts

#### 3. Manage Users
- Create new users
- Promote users to admin
- View user list and roles

#### 4. Monitor Compliance
- View team RTO compliance
- Identify users needing support

## Floor Plan Details

### 9th Floor (214 Seats)
- **CS&S**: Seats 001-120 (120 seats)
- **C2C**: Seats 121-160 (40 seats)
- **Ops Enablement**: Seats 161-186 (26 seats)
- **CS&S (from 10F)**: Seats 187-214 (28 seats)

### 10th Floor (223 Seats)
- **Content Ops + FindLaw**: Seats 001-015 (15 seats)
- **Content Ops + BDR**: Seats 016-060 (45 seats)
- **Content Ops**: Seats 071-105 (45 seats)
- **Product Delivery + AEM, Reuters Tech, Comm Ex**: Seats 106-140 (35 seats)
- **Commentary (Content)**: Seats 141-142 (2 seats)
- **Product Content**: Seats 143-146 (4 seats)
- **Editorial**: Seats 147-180 (32 seats)
- **Editorial / PD Online**: Seats 181-193 (15 seats)

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Reservations
- `GET /api/desks` - Get all desks with availability
- `GET /api/reservations` - Get reservations (filtered)
- `POST /api/reserve` - Create reservation
- `POST /api/reserve/<id>/cancel` - Cancel reservation

### RTO Compliance
- `GET /api/rto-compliance` - Get user's RTO data
- `GET /api/exemptions` - Get user's exemptions
- `POST /api/exemptions` - Add exemption

### Holidays
- `GET /api/holidays` - Get holiday list

### Admin
- `GET /admin/users` - Get all users
- `POST /admin/users` - Create user or promote to admin

## Database Schema

### Tables
- **users** - User accounts and authentication
- **desks** - Workstation information
- **reservations** - Booking records
- **exemptions** - RTO exemption days
- **holidays** - Philippine and company holidays
- **rto_compliance** - Monthly compliance tracking
- **admins** - Admin access list

## Troubleshooting

### Issue: Database not created
**Solution**: Ensure you're in the project directory and run `python app.py`

### Issue: Outlook integration not working
**Solution**: 
1. Verify Azure app credentials in `.env`
2. Check API permissions are granted
3. Ensure `OUTLOOK_ENABLED=True`

### Issue: Can't see floor maps
**Solution**: 
1. Clear browser cache
2. Check browser console for JavaScript errors
3. Ensure static files are loaded correctly

### Issue: Philippine holidays not showing
**Solution**: The system auto-populates on first run. Restart the application.

## Security Best Practices

1. **Change default admin password immediately**
2. **Use strong SECRET_KEY in production**
3. **Enable HTTPS in production**
4. **Keep client secrets secure**
5. **Regularly update dependencies**
6. **Use PostgreSQL for production** (instead of SQLite)
7. **Implement rate limiting** for API endpoints
8. **Regular database backups**

## Production Deployment

### Using Gunicorn (Linux)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Windows
```bash
waitress-serve --port=5000 app:app
```

### Environment Variables for Production
```env
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://user:password@localhost/trmanila_db
OUTLOOK_ENABLED=True
```

## Support & Maintenance

- **Version**: 1.0.0
- **Last Updated**: April 21, 2026
- **Python Version**: 3.8+
- **License**: Proprietary - Thomson Reuters Manila

## Future Enhancements

- [ ] Email notifications for booking confirmations
- [ ] Recurring bookings (daily/weekly)
- [ ] Desk preferences and favorites
- [ ] Analytics dashboard for admins
- [ ] Mobile app (iOS/Android)
- [ ] QR code check-in system
- [ ] Integration with HR systems
- [ ] Export reports (PDF/Excel)

## Credits

Developed for Thomson Reuters Manila office to streamline workstation booking and ensure RTO compliance tracking in hybrid work environments.

---

**For technical support, contact your IT administrator.**