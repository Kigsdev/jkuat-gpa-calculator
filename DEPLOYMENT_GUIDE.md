# Production deployment configuration for JKUAT GPA Calculator

## Environment Setup

### Required Environment Variables

```bash
# Django Configuration
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/jkuat_gpa_prod

# Email Configuration (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Or use SendGrid
# EMAIL_BACKEND=sendgrid_backend.SendgridBackend
# SENDGRID_API_KEY=your-sendgrid-api-key

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Static Files (AWS S3 or similar)
USE_S3=False
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=jkuat-gpa-bucket

# Render/Heroku Deployment
RENDER_EXTERNAL_URL=https://yourdomain.com
```

### Create .env.production file

```bash
cp .env.example .env.production
# Edit with your actual production values
```

## Installation & Setup

### 1. Install PostgreSQL

```bash
# On Render: PostgreSQL is included
# On Heroku: Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0 -a your-app-name

# Locally for testing:
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 2. Create Production Database

```bash
# If using local PostgreSQL for testing
createdb jkuat_gpa_prod
createuser jkuat_prod_user
```

### 3. Install Production Dependencies

```bash
pip install -r requirements.txt
pip install gunicorn
pip install psycopg2-binary
pip install python-decouple
pip install whitenoise  # Static file serving
```

### 4. Generate Secure Secret Key

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Configure Production Settings

Edit `jkuat_gpa/settings.py`:

```python
import os
from pathlib import Path
from decouple import config

# Security
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database
if config('DATABASE_URL', default=None):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='jkuat_gpa_prod'),
            'USER': config('DB_USER', default='jkuat_prod_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# SSL/Security
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Static Files with WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@jkuatgpa.com')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### 6. Prepare for Deployment

```bash
# Collect static files
python manage.py collectstatic --noinput

# Create database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for production
python manage.py createsuperuser

# Run tests one final time
python manage.py test

# Check for security issues
python manage.py check --deploy
```

## Deployment Platforms

### Option A: Deploy to Render

1. Go to https://render.com
2. Connect your GitHub repository
3. Create new Web Service
4. Configure:
   - Runtime: Python 3.12
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn jkuat_gpa.wsgi:application`
5. Add Environment Variables from `.env.production`
6. Deploy PostgreSQL database from Render dashboard
7. Set `DATABASE_URL` to Render PostgreSQL connection string

### Option B: Deploy to Heroku

1. Install Heroku CLI: `brew install heroku` (macOS) or `curl https://cli-assets.heroku.com/install.sh | sh` (Linux)
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Add PostgreSQL: `heroku addons:create heroku-postgresql:standard-0 -a your-app-name`
5. Create `Procfile`:
   ```
   web: gunicorn jkuat_gpa.wsgi:application
   release: python manage.py migrate
   ```
6. Create `runtime.txt`:
   ```
   python-3.12.0
   ```
7. Set environment variables:
   ```bash
   heroku config:set DEBUG=False SECRET_KEY=your-key -a your-app-name
   ```
8. Deploy:
   ```bash
   git push heroku main
   ```
9. Create superuser:
   ```bash
   heroku run python manage.py createsuperuser -a your-app-name
   ```

## Post-Deployment

### 1. Verify Deployment

```bash
# Test the application
curl https://yourdomain.com
curl https://yourdomain.com/admin
curl https://yourdomain.com/accounts/login/

# Check SSL certificate
openssl s_client -connect yourdomain.com:443
```

### 2. Set Up Monitoring

- Sentry (error tracking): https://sentry.io
- New Relic (performance): https://newrelic.com
- Uptime Robot (availability): https://uptimerobot.com

### 3. Configure Email

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password as `EMAIL_HOST_PASSWORD`

**For SendGrid:**
1. Create account at https://sendgrid.com
2. Create API key
3. Install: `pip install sendgrid-django`
4. Set `SENDGRID_API_KEY` environment variable

### 4. Set Up Backups

**PostgreSQL Backups:**
```bash
# Weekly backup script
pg_dump -U jkuat_prod_user jkuat_gpa_prod | gzip > backup_$(date +%Y%m%d).sql.gz

# Store in S3 or cloud storage
```

### 5. DNS Configuration

Point your domain to the deployment:
- **Render**: Use CNAME in DNS settings
- **Heroku**: Use DNS configuration from Heroku dashboard

## Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY is secure and unique
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SSL/TLS certificate installed
- [ ] Email configuration tested
- [ ] Database backups configured
- [ ] Logging enabled
- [ ] Security headers set
- [ ] CSRF protection enabled
- [ ] Admin panel password strong
- [ ] Superuser created
- [ ] Tests passing
- [ ] `check --deploy` passes all checks

## Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput --clear
```

### Database Connection Issues
```bash
python manage.py dbshell  # Test connection
```

### Email Not Sending
- Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
- Test with: `python manage.py shell` then `from django.core.mail import send_mail; send_mail(...)`
- Check email logs

### Application Errors
```bash
# View logs on Render/Heroku
heroku logs --tail -a your-app-name
```

## Rollback Plan

If deployment issues occur:
1. Render: Redeploy previous commit
2. Heroku: `heroku rollback -a your-app-name`
3. Check logs for error details
4. Fix issue locally and redeploy

---

**Next Steps:** Follow the deployment guide for your chosen platform and complete pre-launch checklist.
