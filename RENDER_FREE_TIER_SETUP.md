# Render Deployment Setup - Free Tier with Build Script

## Quick Reference

### 1. Make Script Executable (Run Locally)

```bash
chmod +x build.sh
git add build.sh
git commit -m "feat: add build.sh for Render deployment automation"
git push origin main
```

### 2. Environment Variables for Render Dashboard

Add these 14 environment variables in Render's **Environment** section:

```
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here-min-50-chars
ALLOWED_HOSTS=jkuat-gpa-calculator-1.onrender.com
DATABASE_URL=will-be-set-after-creating-PostgreSQL
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your-strong-password-here
DJANGO_SUPERUSER_EMAIL=your-email@gmail.com
```

### 3. Render Build Command

**Copy this EXACTLY into the Build Command field:**

```bash
chmod +x build.sh && ./build.sh
```

### 4. Render Start Command

```bash
gunicorn jkuat_gpa.wsgi:application
```

---

## Step-by-Step Deployment Instructions

### Step 1: Push Updated Code

```bash
cd /home/jonnykigs/Desktop/Project
chmod +x build.sh
git add build.sh
git commit -m "feat: add automated build script for Render deployment"
git push origin main
```

### Step 2: Create Render Web Service

1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. Select `jkuat-gpa-calculator` repository
4. **Name**: `jkuat-gpa-calculator-1`
5. **Environment**: Python 3
6. **Region**: Frankfurt (or closest to you)
7. **Plan**: Free

### Step 3: Configure Build & Start Commands

1. **Build Command**:
   ```
   chmod +x build.sh && ./build.sh
   ```

2. **Start Command**:
   ```
   gunicorn jkuat_gpa.wsgi:application
   ```

3. Click **Create Web Service**

### Step 4: Add Environment Variables

While the build runs, scroll down to **Environment** section and add all 17 variables:

**Security Variables:**
- `DEBUG` = `False`
- `SECRET_KEY` = [Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`]
- `ALLOWED_HOSTS` = `jkuat-gpa-calculator-1.onrender.com`

**Email Variables:**
- `EMAIL_BACKEND` = `django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST` = `smtp.gmail.com`
- `EMAIL_PORT` = `587`
- `EMAIL_USE_TLS` = `True`
- `EMAIL_HOST_USER` = [Your Gmail address]
- `EMAIL_HOST_PASSWORD` = [Gmail App Password - from https://myaccount.google.com/apppasswords]
- `DEFAULT_FROM_EMAIL` = [Same as EMAIL_HOST_USER]

**Security Headers:**
- `SECURE_SSL_REDIRECT` = `True`
- `SESSION_COOKIE_SECURE` = `True`
- `CSRF_COOKIE_SECURE` = `True`
- `SECURE_HSTS_SECONDS` = `31536000`

**Superuser Credentials (for auto-creation):**
- `DJANGO_SUPERUSER_USERNAME` = `admin`
- `DJANGO_SUPERUSER_PASSWORD` = [Strong password - min 8 chars]
- `DJANGO_SUPERUSER_EMAIL` = [Your email]

**Database (Set After PostgreSQL Creation):**
- `DATABASE_URL` = [Will be set in Step 5]

### Step 5: Create PostgreSQL Database

1. Click **New +** → **PostgreSQL**
2. **Name**: `jkuat-gpa-db`
3. **Database**: `jkuat_gpa_prod`
4. **Region**: Same as Web Service
5. **Plan**: Free
6. Click **Create Database**
7. Wait 2-3 minutes for "Available" status
8. Copy **Internal Database URL**

### Step 6: Link Database to Web Service

1. Go back to Web Service
2. Scroll to **Environment Variables**
3. Add new variable:
   - **Key**: `DATABASE_URL`
   - **Value**: [Paste Internal Database URL]
4. Save

### Step 7: Deploy

The deployment will automatically:
- ✅ Install dependencies from `requirements.txt`
- ✅ Collect static files
- ✅ Run database migrations
- ✅ Create superuser (if credentials provided)
- ✅ Start Gunicorn server

Monitor progress in **Logs** section. Wait for: `"Successfully started service"`

### Step 8: Access Your Application

Once deployment completes:

- **Application**: `https://jkuat-gpa-calculator-1.onrender.com`
- **Admin Panel**: `https://jkuat-gpa-calculator-1.onrender.com/admin/`
- **Login with**:
  - **Username**: `admin` (or your DJANGO_SUPERUSER_USERNAME)
  - **Password**: Your DJANGO_SUPERUSER_PASSWORD

---

## What the build.sh Script Does

### 1. **Error Handling**
```bash
set -e  # Exits immediately if any command fails
```
Prevents broken deployments from continuing.

### 2. **Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
Installs all packages your Django app needs (Django, psycopg2, gunicorn, reportlab, etc.)

### 3. **Collect Static Files**
```bash
python manage.py collectstatic --noinput --clear
```
Gathers CSS, JavaScript, images from all apps and serves them efficiently on Render.

### 4. **Run Migrations**
```bash
python manage.py migrate --noinput
```
Updates your PostgreSQL database schema to match your models.

### 5. **Create Superuser (Idempotent)**
```bash
python manage.py shell << END
# Checks if superuser exists before creating
# If exists, skips creation without error
# If not, creates with provided credentials
END
```
Creates admin account automatically **without** requiring Shell access.

---

## Troubleshooting

### Build Script Fails

**Check Logs**:
1. Go to Web Service → **Logs**
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Syntax errors in code
   - Wrong Python version

**Fix**:
```bash
# Test locally first
python manage.py check --deploy
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### Superuser Not Created

**If build.sh doesn't create superuser**:
1. Check these variables are set on Render:
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_PASSWORD`
   - `DJANGO_SUPERUSER_EMAIL`
2. If missing, add them and redeploy
3. Or register manually at `/accounts/register/`

### Static Files Not Loading (No CSS/Images)

**Solution**:
1. Verify `STATIC_ROOT` and `STATIC_URL` in settings.py
2. Check Web Service logs for collectstatic errors
3. Trigger rebuild: Go to Web Service → **Deploy** button

### Database Connection Error

**Error**: `could not connect to server`

**Fix**:
1. Verify `DATABASE_URL` is set correctly
2. Check PostgreSQL shows "Available" status
3. Use **Internal** Database URL (not External)
4. Redeploy Web Service after setting DATABASE_URL

### Email Not Sending

**Check**:
1. Gmail account is correct
2. App Password is 16 chars (no spaces) - from myaccount.google.com/apppasswords
3. EMAIL_HOST = `smtp.gmail.com`
4. EMAIL_PORT = `587`
5. EMAIL_USE_TLS = `True`

---

## File Checklist

- ✅ `build.sh` - Automated build script (created)
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Heroku/Render config
- ✅ `runtime.txt` - Python version
- ✅ `.github/workflows/ci-cd.yml` - Automated testing
- ✅ `jkuat_gpa/settings.py` - Django configuration

All files ready for deployment!

---

## Post-Deployment Checklist

- [ ] Application loads at `https://jkuat-gpa-calculator-1.onrender.com`
- [ ] Admin panel accessible
- [ ] Can login with superuser credentials
- [ ] Dashboard displays correctly
- [ ] PDF export works
- [ ] Analytics page loads
- [ ] Email notifications send
- [ ] Database backups enabled

---

## Monitoring & Maintenance

### View Real-Time Logs
Web Service → **Logs** (see what's happening live)

### Check Performance
Web Service → **Metrics** (CPU, memory, network)

### Enable Monitoring
1. Go to account → **Notifications**
2. Enable email alerts
3. Get notified if service crashes

### Auto-Deploy on Code Push (Optional)
Web Service → Settings → **Auto-Deploy** → Turn ON

Now every GitHub push triggers automatic deployment!

---

## Success! 🚀

Your JKUAT GPA Calculator is deployed with:
- ✅ Fully automated setup (no manual Shell commands)
- ✅ Automatic superuser creation
- ✅ Environment-based configuration
- ✅ Production-ready security settings
- ✅ Ready for immediate use

**Next**: Login to admin and add students/grades!
