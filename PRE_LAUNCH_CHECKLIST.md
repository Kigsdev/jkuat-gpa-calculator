# Phase 6: Pre-Launch Checklist

Complete all items before deploying to production.

## ✅ Security Checklist

### Django Settings
- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is unique and secure (50+ characters)
- [ ] `ALLOWED_HOSTS` configured with your domain
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SECURE_HSTS_SECONDS` set to 31536000 (1 year)
- [ ] `SECURE_HSTS_PRELOAD = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `X_FRAME_OPTIONS = 'DENY'`
- [ ] Security headers configured (Content-Security-Policy, etc.)

### Run Security Checks
```bash
python manage.py check --deploy
# All issues must be resolved
```

## ✅ Database Checklist

### PostgreSQL Setup
- [ ] PostgreSQL 12+ installed
- [ ] Database created: `jkuat_gpa_prod`
- [ ] Database user created with strong password
- [ ] Database backups configured
- [ ] Connection tested: `psql -U user -d jkuat_gpa_prod`

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
# All migrations applied successfully
```

- [ ] All migrations applied
- [ ] No pending migrations
- [ ] Database schema verified

## ✅ Static Files Checklist

### Collect Static Files
```bash
python manage.py collectstatic --noinput --clear
```

- [ ] All static files collected
- [ ] CSS files present
- [ ] JavaScript files present
- [ ] Images present
- [ ] StaticFiles storage configured

## ✅ Email Configuration Checklist

### Gmail Setup (Recommended for Production)
- [ ] 2-Factor Authentication enabled on Gmail account
- [ ] App Password generated
- [ ] `EMAIL_HOST_USER` set to Gmail address
- [ ] `EMAIL_HOST_PASSWORD` set to App Password
- [ ] Email settings in `.env` file

### Email Testing
```bash
python manage.py shell
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test',
    'your-email@gmail.com',
    ['your-email@gmail.com'],
    fail_silently=False,
)
```

- [ ] Test email sent and received
- [ ] Email templates render correctly
- [ ] Password reset emails work
- [ ] Email notifications configured

## ✅ Testing Checklist

### Unit Tests
```bash
python manage.py test academics accounts --verbosity=2
```

- [ ] All tests passing (24+ tests)
- [ ] No regressions
- [ ] Coverage > 80%

### Manual Testing
- [ ] Login with test credentials works
- [ ] Dashboard displays correctly
- [ ] PDF export generates without errors
- [ ] Analytics page loads
- [ ] Alerts system working
- [ ] Admin panel accessible
- [ ] Profile updates work
- [ ] Logout works correctly

### Security Testing
- [ ] CSRF protection enabled
- [ ] SQL injection protection verified
- [ ] XSS protection verified
- [ ] Authentication required for all protected pages
- [ ] Session timeout working

## ✅ Deployment Platform Checklist

### Render Deployment
- [ ] GitHub repository connected to Render
- [ ] Environment variables configured
- [ ] PostgreSQL database created
- [ ] Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- [ ] Start command: `gunicorn jkuat_gpa.wsgi:application`
- [ ] Auto-deploy from main branch enabled
- [ ] SSL certificate installed (Render provides free)

### Heroku Deployment
- [ ] Procfile created and committed
- [ ] runtime.txt created with Python version
- [ ] PostgreSQL addon installed
- [ ] Environment variables set via Heroku dashboard
- [ ] `git push heroku main` works
- [ ] Logs show successful deployment
- [ ] Superuser created on Heroku

### General
- [ ] Domain configured
- [ ] SSL/TLS certificate installed (HTTPS)
- [ ] CDN configured (optional)

## ✅ Domain & DNS Checklist

### Domain Setup
- [ ] Domain registered
- [ ] DNS records created pointing to deployment platform
- [ ] DNS propagation verified (usually 24-48 hours)
- [ ] SSL certificate valid and not expired
- [ ] HTTPS working (https://yourdomain.com)
- [ ] HTTP redirects to HTTPS

### Testing
```bash
# Test HTTPS
curl -I https://yourdomain.com

# Test DNS
nslookup yourdomain.com

# Test SSL certificate
openssl s_client -connect yourdomain.com:443
```

- [ ] All tests passing

## ✅ Monitoring & Logging Checklist

### Logging Setup
- [ ] Application logs enabled
- [ ] Error logs configured
- [ ] Log files stored securely
- [ ] Log rotation configured

### Monitoring Setup (Optional but Recommended)
- [ ] Sentry account created (error tracking)
- [ ] Sentry DSN configured in settings
- [ ] New Relic account created (performance monitoring)
- [ ] Uptime Robot monitoring configured
- [ ] Alert notifications configured

### Testing
- [ ] Logs accessible and readable
- [ ] Errors captured in monitoring
- [ ] Notifications working

## ✅ Backup & Recovery Checklist

### Database Backups
- [ ] Automated daily backups configured
- [ ] Backup retention policy set (minimum 30 days)
- [ ] Backup location secure (S3, Dropbox, etc.)
- [ ] Restore process tested and documented

### Disaster Recovery Plan
- [ ] Rollback procedure documented
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined

## ✅ Documentation Checklist

- [ ] README.md updated for production
- [ ] DEPLOYMENT_GUIDE.md completed
- [ ] Environment setup instructions clear
- [ ] Troubleshooting guide created
- [ ] Admin user guide created
- [ ] User guide for students created

## ✅ Legal & Compliance Checklist

- [ ] Privacy policy created and linked
- [ ] Terms of service created and linked
- [ ] Cookie policy implemented (GDPR compliant)
- [ ] Contact/support email configured
- [ ] Data protection measures documented

## ✅ Performance Checklist

### Performance Testing
```bash
# Load testing with Apache Bench
ab -n 1000 -c 100 https://yourdomain.com/

# Response time should be < 2 seconds
# Database queries optimized with select_related()
```

- [ ] Page load time < 2 seconds
- [ ] Admin panel responsive
- [ ] PDF generation fast enough
- [ ] Analytics dashboard performs well
- [ ] Database queries optimized

## ✅ Final Pre-Launch Checklist

### 48 Hours Before Launch
- [ ] All checklist items completed
- [ ] Smoke testing passed
- [ ] Team notified of launch time
- [ ] Backup verified
- [ ] Rollback plan reviewed

### 24 Hours Before Launch
- [ ] Final security scan
- [ ] Performance test successful
- [ ] Monitoring alerts configured
- [ ] Support team trained
- [ ] Emergency contacts documented

### 1 Hour Before Launch
- [ ] Team on standby
- [ ] Monitoring dashboard open
- [ ] Logs being tailed
- [ ] Rollback plan ready
- [ ] Communication channels open

### Launch Day (Go-Live)
- [ ] Domain DNS points to production
- [ ] Application accessible at yourdomain.com
- [ ] Admin panel working
- [ ] Student accounts can login
- [ ] Email notifications sending
- [ ] Analytics tracking data
- [ ] Monitoring shows no errors
- [ ] Performance metrics normal

### Post-Launch (First 24 Hours)
- [ ] Monitor logs closely
- [ ] Check for errors in Sentry
- [ ] Verify email delivery
- [ ] Monitor database performance
- [ ] User feedback collection
- [ ] Document any issues

## Rollback Plan

If critical issues occur after launch:

1. **Immediate Response** (First 5 minutes)
   - Acknowledge issue in monitoring dashboard
   - Notify team
   - Check logs for error patterns

2. **Diagnosis** (5-15 minutes)
   - Review error messages
   - Check database connectivity
   - Verify email service
   - Review recent changes

3. **Rollback Decision**
   - If database issue: Render `Redeploy` or Heroku `rollback`
   - If code issue: Git revert + redeploy
   - If config issue: Update environment variables and redeploy

4. **Rollback Execution**
   ```bash
   # Heroku
   heroku rollback -a your-app-name
   
   # Render
   Manually redeploy previous commit from dashboard
   
   # Manual
   git revert HEAD
   git push origin main
   ```

5. **Post-Rollback**
   - Verify application working
   - Notify stakeholders
   - Schedule fix for later
   - Document issue and resolution

## Success Criteria

✅ Application accessible at production domain
✅ All tests passing
✅ No errors in logs for 24 hours
✅ Users successfully logging in
✅ Emails sending correctly
✅ PDF exports working
✅ Analytics tracking data
✅ Backups running
✅ Monitoring alerts configured
✅ Performance metrics within target

---

**Status**: Phase 6 Ready for Deployment
**Last Updated**: January 11, 2026
**Next Step**: Follow deployment platform guide and complete final checklist

Congratulations! Your JKUAT GPA Calculator is ready for production! 🚀
