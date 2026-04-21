# Quick Start Guide - TR Manila Workstation Reservation System

Get up and running in 5 minutes!

## 🚀 Fast Setup (Windows)

### 1. Open Command Prompt/PowerShell
```powershell
cd Desktop\tr-manila-workstation-app
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Create .env File
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

Edit `.env` and set a secret key (or use default for testing):
```env
SECRET_KEY=my-test-secret-key-12345
DATABASE_URL=sqlite:///tr_manila_workstation.db
OUTLOOK_ENABLED=False
```

### 5. Run Application
```powershell
python app.py
```

### 6. Open Browser
Navigate to: **http://localhost:5000**

### 7. Login
**Default Admin Account:**
- Email: `admin@tr-manila.com`
- Password: `Admin@123`

**⚠️ IMPORTANT**: Change this password immediately after first login!

---

## 📋 What You'll See

### Dashboard
- RTO Compliance tracker
- Quick booking options
- My upcoming reservations
- Exemption management

### Floor Map
- Interactive 9th and 10th floor maps
- 437 total workstations
- Real-time availability
- Click-to-book interface

---

## 👤 Create Your First User Account

1. Click **"Register here"** on login page
2. Fill in:
   - Full Name
   - Username
   - Email (use your corporate email)
   - Password
3. Click **Register**
4. Login with new credentials

---

## 🎯 Make Your First Booking

1. Go to **Floor Map**
2. Select tomorrow's date
3. Choose time slot (Full Day, Morning, or Afternoon)
4. Click **Check Availability**
5. Click any **green seat** (available)
6. Review details
7. Click **Confirm Booking**
8. Done! ✅

---

## 📊 Track RTO Compliance

Dashboard automatically shows:
- **In-Office Days**: Days you booked a desk
- **Available Days**: Weekdays minus holidays and exemptions
- **Compliance %**: (In-Office ÷ Available) × 5
- **Target**: 5/5 (100%)

---

## 🔧 Common Commands

### Start Application
```powershell
python app.py
```

### Stop Application
Press `Ctrl + C` in terminal

### Restart Application
1. `Ctrl + C` to stop
2. `python app.py` to start

### Access from Other Devices (Same Network)
```powershell
python app.py
# Note the IP address shown, e.g., http://192.168.1.100:5000
```

---

## 📱 Mobile Access

The application is mobile-responsive! Access from:
- Smartphones
- Tablets
- Any device with a web browser

---

## 🆘 Troubleshooting

### Issue: "python is not recognized"
**Solution**: Install Python 3.8+ from python.org

### Issue: Port 5000 already in use
**Solution**: Change port in app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

### Issue: Can't install packages
**Solution**: Update pip first:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Database errors
**Solution**: Delete database file and restart:
```powershell
del tr_manila_workstation.db
python app.py
```

---

## 🎓 Next Steps

1. ✅ Change default admin password
2. ✅ Create user accounts for your team
3. ✅ Make test bookings
4. ✅ Test RTO compliance tracking
5. 📖 Read full README.md for advanced features
6. 🔐 Set up Microsoft 365 integration (optional)

---

## 📞 Support

For detailed documentation, see **README.md**

For Microsoft 365 setup, see **README.md** section "Microsoft 365 Integration Setup"

---

**Enjoy your streamlined workstation booking experience! 🎉**