# Render Deployment - Quick Reference Checklist

## ✅ Pre-Deployment (5 minutes)

### Prepare Your Machine
- [ ] Generate SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] Save SECRET_KEY to notepad
- [ ] Get Gmail App Password from https://myaccount.google.com/apppasswords
- [ ] Save App Password to notepad

### Verify Code Ready
```bash
cd /home/jonnykigs/Desktop/Project
source venv/bin/activate
python manage.py test academics accounts  # All 24 tests should pass
python manage.py check --deploy  # Should report 0 issues
python manage.py collectstatic --noinput  # Should collect successfully
```

- [ ] All tests passing
- [ ] No Django check warnings
- [ ] Static files collected
- [ ] Git committed: `git status` shows clean
- [ ] Latest changes pushed: `git push origin main`

## 🚀 Render Deployment (15-20 minutes)

### Step 1: Create Render Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize GitHub access

### Step 2: Create Web Service
- [ ] Click **New +** → **Web Service**
- [ ] Connect `jkuat-gpa-calculator` repository
- [ ] Wait for connection confirmation

### Step 3: Configure Web Service
```
Name: jkuat-gpa-calculator
Environment: Python 3
Region: (closest to users)
Plan: Free (or Starter for production)

Build Command:
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

Start Command:
gunicorn jkuat_gpa.wsgi:application
```

- [ ] Name set
- [ ] Python 3 selected
- [ ] Region selected
- [ ] Plan chosen
- [ ] Build command pasted exactly
- [ ] Start command pasted exactly

### Step 4: Add Environment Variables
Click **Add Environment Variable** for each:

```
DEBUG = False
SECRET_KEY = [paste your generated key here]
ALLOWED_HOSTS = jkuat-gpa-calculator.onrender.com
EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = your-email@gmail.com
EMAIL_HOST_PASSWORD = [paste app password here - no spaces]
DEFAULT_FROM_EMAIL = your-email@gmail.com
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

- [ ] All 14 variables added
- [ ] No typos in keys
- [ ] No extra spaces in passwords

### Step 5: Create PostgreSQL Database
- [ ] Click **New +** → **PostgreSQL**
- [ ] Name: `jkuat-gpa-db`
- [ ] Database: `jkuat_gpa_prod`
- [ ] Region: Same as Web Service
- [ ] Plan: Free
- [ ] Click **Create Database**
- [ ] Wait 2-3 minutes for "Available" status
- [ ] Copy **Internal Database URL**

### Step 6: Link Database to Web Service
- [ ] Go back to Web Service
- [ ] Click **Environment** section
- [ ] Click **Add Environment Variable**
- [ ] Key: `DATABASE_URL`
- [ ] Value: [Paste Internal Database URL]
- [ ] Save

### Step 7: Deploy
- [ ] Scroll to top of Web Service
- [ ] Click **Deploy** button
- [ ] Monitor **Logs** section
- [ ] Wait for: "Successfully started service"
- [ ] Note your URL: `https://jkuat-gpa-calculator.onrender.com`

### Step 8: Create Superuser
- [ ] Click **Shell** button (top right)
- [ ] Run: `python manage.py createsuperuser`
- [ ] Username: `admin`
- [ ] Email: `your-email@gmail.com`
- [ ] Password: `[your strong password]`
- [ ] Confirm password: `[same password]`

## ✅ Post-Deployment Testing (10 minutes)

### Test Application Access
- [ ] Homepage loads: https://jkuat-gpa-calculator.onrender.com
- [ ] Admin accessible: https://jkuat-gpa-calculator.onrender.com/admin/
- [ ] Admin login works with superuser credentials
- [ ] Student login page loads: /accounts/login/

### Test Student Features
- [ ] Login with `SCT211-0001/2021` / `password123`
- [ ] Dashboard displays GPA
- [ ] Transcript page accessible
- [ ] Units page shows grades
- [ ] Projection page displays targets
- [ ] Analytics page loads
- [ ] PDF export works (click Export button)
- [ ] Alerts page displays

### Test Admin Features
- [ ] Add new student in admin
- [ ] Add new unit in admin
- [ ] Add grade/result in admin
- [ ] View all models

### Test Email
- [ ] Try password reset flow
- [ ] Check if email received
- [ ] Email contains reset link
- [ ] Link works

## 🔒 Security Verification

- [ ] HTTPS working (padlock icon in browser)
- [ ] No warnings about mixed content
- [ ] DEBUG is False (not showing error details)
- [ ] Admin accessible only with login
- [ ] CSRF protection working (test form submission)

## 📊 Monitoring Setup (Optional but Recommended)

### Sentry Error Tracking
- [ ] Go to https://sentry.io
- [ ] Create free account
- [ ] Create Django project
- [ ] Copy Sentry DSN
- [ ] Add to Web Service environment: `SENTRY_DSN = [your-dsn]`

### Uptime Monitoring
- [ ] Go to https://uptimerobot.com
- [ ] Create free account
- [ ] Add monitor for your URL
- [ ] Receive alerts if site goes down

## 🎉 Done!

Your application is now deployed and running on Render!

### Share These URLs:
- **Live App**: https://jkuat-gpa-calculator.onrender.com
- **Admin**: https://jkuat-gpa-calculator.onrender.com/admin/
- **Documentation**: Check RENDER_DEPLOYMENT.md for troubleshooting

### Default Test Credentials:
```
Registration Number: SCT211-0001/2021
Password: password123
```

### Common Issues & Quick Fixes:

**Build Failed?**
- Check logs for error message
- Ensure `requirements.txt` is committed
- Verify Python syntax is correct

**Can't Access App?**
- Wait 5 minutes for deployment to complete
- Check Logs for errors
- Verify all environment variables set

**Email not sending?**
- Verify EMAIL_HOST_PASSWORD has no spaces
- Confirm Gmail App Password is correct
- Check Gmail 2FA is enabled

**Database error?**
- Verify DATABASE_URL is set correctly
- Check PostgreSQL is "Available"
- Ensure Internal URL (not External) is used

---

**Deployment Time**: ~15-20 minutes
**Estimated Cost**: FREE (Render free tier)
**Go-Live Status**: ✅ LIVE

Congratulations! Your JKUAT GPA Calculator is now on Render! 🚀
