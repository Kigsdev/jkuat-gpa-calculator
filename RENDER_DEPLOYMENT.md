# Deploy JKUAT GPA Calculator to Render - Step-by-Step Guide

## Prerequisites

- GitHub account with your repository pushed
- Render account (free at https://render.com)
- Email configured for notifications
- About 15-20 minutes

## Step 1: Create Render Account & Connect GitHub

1. Go to https://render.com
2. Click **Sign up** (or log in if you have an account)
3. Select **Continue with GitHub** (recommended)
4. Authorize Render to access your GitHub repositories
5. You'll be redirected to Render dashboard

## Step 2: Create a New Web Service

1. On Render dashboard, click **New +** button (top right)
2. Select **Web Service**
3. Find your repository: `jkuat-gpa-calculator`
4. Click **Connect** next to the repository name
5. If not listed, click **Connect Account** to authorize more GitHub repos

## Step 3: Configure Web Service Settings

### Basic Information

- **Name**: `jkuat-gpa-calculator` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**:
  ```
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```
- **Start Command**:
  ```
  gunicorn jkuat_gpa.wsgi:application
  ```

### Plan

- Select **Free** plan (good for testing)
- Or **Starter** ($7/month) for production

### Region

- Select closest region to your users (e.g., `Frankfurt`, `Cincinnati`)

## Step 4: Configure Environment Variables

1. Scroll down to **Environment** section
2. Click **Add Environment Variable**
3. Add the following variables:

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
```

### To Generate SECRET_KEY:

```bash
# Run locally:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste as SECRET_KEY value.

### Gmail App Password Setup:

1. Go to https://myaccount.google.com/apppasswords
2. Select **Mail** and **Windows** (or your device)
3. Click **Generate**
4. Copy the 16-character password
5. Use as `EMAIL_HOST_PASSWORD` (remove spaces)

## Step 5: Create PostgreSQL Database

1. On Render dashboard, click **New +** button again
2. Select **PostgreSQL**
3. Configure:
   - **Name**: `jkuat-gpa-db`
   - **Database**: `jkuat_gpa_prod`
   - **User**: Keep default or set custom
   - **Region**: Same as Web Service
   - **Version**: 15 (latest stable)
   - **Plan**: Free (or Starter for production)
4. Click **Create Database**

### Wait for Database Creation (2-3 minutes)

- You'll see status changing to "Available"
- Copy the **Internal Database URL** (you'll need this)

## Step 6: Link Database to Web Service

1. Go back to your Web Service
2. Scroll to **Environment Variables**
3. Click **Add Environment Variable**
4. **Key**: `DATABASE_URL`
5. **Value**: Paste the Internal Database URL from PostgreSQL
   - Format: `postgresql://user:password@hostname:5432/jkuat_gpa_prod`

## Step 7: Deploy Web Service

1. Scroll to top of Web Service page
2. Click **Deploy** button
3. Monitor the deployment in the **Logs** section
4. Wait for message: `"Successfully started service"`

### What Happens During Deployment:

- ✅ Installs Python dependencies
- ✅ Collects static files
- ✅ Runs database migrations
- ✅ Starts Gunicorn server
- ⏱️ Takes 3-5 minutes

## Step 8: Create Superuser

Once deployment is successful:

1. Click on your Web Service
2. Click **Shell** (top right)
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts:
   - **Username**: admin
   - **Email**: your-email@gmail.com
   - **Password**: Create strong password
   - **Confirm password**: Repeat password

## Step 9: Access Your Application

Your app is now live! Access it at:

- **Application**: `https://jkuat-gpa-calculator.onrender.com` (or your custom name)
- **Admin Panel**: `https://jkuat-gpa-calculator.onrender.com/admin/`
- **Student Login**: `https://jkuat-gpa-calculator.onrender.com/accounts/login/`

## Step 10: Configure Custom Domain (Optional)

If you have a custom domain:

1. Go to Web Service settings
2. Scroll to **Custom Domain**
3. Enter your domain (e.g., `gpa.yourdomain.com`)
4. Click **Add Custom Domain**
5. Configure DNS records in your domain provider:
   - **Type**: CNAME
   - **Name**: `gpa` (or subdomain)
   - **Value**: Your Render URL
   - Wait 15-30 minutes for DNS propagation

## Troubleshooting

### Build Failed

**Error**: `Command exited with non-zero status code`

- **Fix**: Check logs for specific error
- Common issues:
  - Missing requirements in `requirements.txt`
  - Syntax errors in code
  - Wrong Python version

**Solution**:

```bash
# Test locally first
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py check --deploy
```

### Application Not Starting

**Error**: `Web service failed to start`

- **Fix**: Check Shell logs for errors
- Common issues:
  - Database connection problem
  - Wrong SECRET_KEY format
  - Missing environment variables

**Solution**:

1. Click **Shell**
2. Run: `python manage.py check`
3. Fix any issues shown

### Static Files Not Loading (CSS/JS not showing)

**Error**: CSS/images show 404 errors

- **Fix**: Collect static files again

```bash
# In Shell:
python manage.py collectstatic --clear --noinput
```

### Database Connection Error

**Error**: `could not connect to server`

- **Fix**: Verify DATABASE_URL is correct
- Check PostgreSQL is still running
- Ensure DATABASE_URL matches exactly

### Email Not Sending

**Error**: `SMTPAuthenticationError` or `Connection refused`

- **Fix**: Verify email credentials
  1. Gmail account is correct
  2. App Password is correct (16 chars, no spaces)
  3. EMAIL_HOST is `smtp.gmail.com`
  4. EMAIL_PORT is `587`
  5. EMAIL_USE_TLS is `True`

### Superuser Login Failing

**Error**: Cannot login with superuser credentials

- **Fix**: Recreate superuser

```bash
# In Shell:
python manage.py shell
from django.contrib.auth.models import User
User.objects.filter(username='admin').delete()
exit()
# Then run createsuperuser again
```

## Post-Deployment Checklist

- [ ] Application accessible at HTTPS
- [ ] Admin panel working (create test admin)
- [ ] Student login works (test with sample credentials)
- [ ] Dashboard displays GPA correctly
- [ ] PDF export works
- [ ] Analytics page loads
- [ ] Email sends successfully
- [ ] Alerts system working
- [ ] Database backups configured (see below)

## Enable Database Backups (Recommended)

1. Go to PostgreSQL resource on Render
2. Scroll to **Backups**
3. Enable **Backups** (toggle on)
4. Set retention to 30 days minimum
5. Backups automatically run daily

## Monitor Your Deployment

### View Logs

1. Click your Web Service
2. Scroll to **Logs**
3. See real-time application logs

### Set Up Email Alerts

1. Go to account settings (top right)
2. Click **Notifications**
3. Enable **Email notifications**
4. Get alerts if service goes down

### Performance Metrics

1. Click your Web Service
2. See CPU, memory, network usage
3. Monitor for unusual activity

## Update Your Application

When you push new code to GitHub:

1. Changes automatically detected
2. New deployment triggered
3. Monitor progress in Logs
4. New version live in 3-5 minutes

**Enable Auto-Deploy (optional):**

- Web Service settings → **Auto-Deploy** → On
- Automatically redeploy on every GitHub push

## Scale Your Application (If Needed)

If you need better performance:

1. Go to Web Service settings
2. Upgrade plan from Free to Starter or Pro
3. Render automatically restarts with more resources

## Success! 🎉

Your JKUAT GPA Calculator is now deployed on Render!

### Important URLs:

- **Application**: `https://jkuat-gpa-calculator.onrender.com`
- **Admin**: `https://jkuat-gpa-calculator.onrender.com/admin/`
- **Render Dashboard**: `https://dashboard.render.com`

### Test Credentials:

- **Registration Number**: SCT211-0001/2021
- **Password**: password123

### Next Steps:

1. ✅ Test all features
2. ✅ Configure monitoring (Sentry for errors)
3. ✅ Set up uptime monitoring (Uptime Robot)
4. ✅ Configure custom domain if you have one
5. ✅ Share with JKUAT users!

---

**Need Help?**

- Check Render logs: Web Service → Logs
- Check Shell for errors: Web Service → Shell
- Review application logs: `python manage.py shell`
- Email support: Check your notifications

**Deployment Complete!** 🚀
