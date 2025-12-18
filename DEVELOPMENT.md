# Development Setup Guide

## Quick Start

### 1. Clone the Project
```bash
git clone <repository-url>
cd Project
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (already set for development)
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`
Admin panel at `http://localhost:8000/admin`

## Database Management

### Create Sample Data
```bash
python manage.py shell
```

Then run:
```python
from accounts.models import Student
from academics.models import AcademicYear, Unit, Result
from django.contrib.auth.models import User
from datetime import datetime

# Create academic year
ay = AcademicYear.objects.create(year=2024, semester=1, is_active=True)

# Create units
Unit.objects.create(code='MIT201', name='Data Structures', credit_units=3, academic_year=ay)
Unit.objects.create(code='MIT202', name='Web Development', credit_units=4, academic_year=ay)

# Create a student (after creating a user first)
user = User.objects.create_user(username='student1', password='password123')
student = Student.objects.create(
    user=user,
    registration_number='SCT211-0001/2021',
    course='Bachelor of Science in Computer Science',
    year_of_study=2,
    academic_year='2024/2025'
)

# Add grades
units = Unit.objects.filter(academic_year=ay)
Result.objects.create(student=student, unit=units[0], score=78)
Result.objects.create(student=student, unit=units[1], score=85)

exit()
```

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test accounts
python manage.py test academics
```

### Run With Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Creates htmlcov/index.html
```

## Debugging

### Django Shell
```bash
python manage.py shell
```

### Print SQL Queries
Add to settings.py:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Access Django ORM
```bash
python manage.py shell
```

```python
from accounts.models import Student
from academics.utils import GradeCalculator

# Get all students
students = Student.objects.all()

# Get a specific student and calculate GPA
student = students.first()
gpa_data = GradeCalculator.calculate_wma(student)
print(f"GPA: {gpa_data['gpa']}")
print(f"Honors: {gpa_data['honors_level']}")
```

## Deployment Checklist

- [ ] Set DEBUG = False in production
- [ ] Update ALLOWED_HOSTS with production domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong SECRET_KEY
- [ ] Configure HTTPS
- [ ] Set up database backups
- [ ] Configure email settings
- [ ] Set up logging
- [ ] Run security checks: `python manage.py check --deploy`

## Common Issues

### Migration Conflicts
```bash
python manage.py migrate --fake <app> <migration>
```

### Clear All Data
```bash
python manage.py flush
```

### Recreate Database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Version Control

### Create a new branch
```bash
git checkout -b feature/feature-name
```

### Commit changes
```bash
git add .
git commit -m "Feature: Description of changes"
git push origin feature/feature-name
```

### Create Pull Request
- Go to GitHub and create a PR for review

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [JKUAT Portal](https://jkuat.ac.ke/)

## Support

For issues or questions, contact the development team or create an issue on GitHub.

---

**Last Updated**: December 18, 2024
**Version**: 1.0
