# 🚀 JKUAT GPA Calculator - Quick Start Guide

## What Has Been Built

A complete Django-based academic tracking system for JKUAT students featuring:
- ✅ Secure login with registration numbers
- ✅ GPA calculation using JKUAT grading standards
- ✅ Academic dashboard with visualizations
- ✅ Complete student database with sample data
- ✅ Professional UI with Bootstrap 5
- ✅ Admin panel for managing students and grades
- ✅ Projection engine for graduation planning

## Installation & Launch (< 5 minutes)

### Step 1: Navigate to Project
```bash
cd "/home/jonnykigs/Desktop/Project"
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 3: Start Development Server
```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 4: Access the Application
- **Home Page**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin (use superuser credentials)
- **Student Login**: http://localhost:8000/accounts/login/

---

## 🔐 Test Credentials

Use any of these to login:

| Registration Number | Name | GPA | Honors |
|---|---|---|---|
| SCT211-0001/2021 | John Njogu | 83.95 | First Class |
| SCT211-0002/2021 | Roy Kipchoge | 70.86 | First Class |
| SCT211-0003/2021 | Vivian Muthoni | 94.48 | First Class |
| SCT211-0004/2021 | Apphie Kimani | 49.24 | Pass |

**Password for all**: `password123`

---

## 📱 Key Features to Explore

### 1. Login Page
- URL: http://localhost:8000/accounts/login/
- Features:
  - Registration number-based login
  - Help modal for forgot credentials
  - Professional JKUAT branding

### 2. Dashboard
- URL: http://localhost:8000/academics/dashboard/
- Shows:
  - Current GPA
  - Honors level badge
  - Grade distribution chart
  - Units completed
  - Quick links to other sections

### 3. Admin Panel
- URL: http://localhost:8000/admin/
- Create superuser first: `python manage.py createsuperuser`
- Features:
  - Manage students
  - Add/edit unit grades
  - View academic years
  - GPA tracking

---

## 📊 Project Structure

```
Project/
├── academics/           # GPA logic & calculations
├── accounts/            # User authentication
├── templates/           # HTML pages
├── jkuat_gpa/          # Django settings
├── manage.py           # Django control
├── requirements.txt    # Dependencies
├── seed_data.py        # Sample data script
├── README.md           # Full documentation
└── DEVELOPMENT.md      # Dev guide
```

---

## 🔍 What's Implemented

### Database Models ✅
- Student (with registration number)
- AcademicYear
- Unit
- Result (scores & grades)
- GPACalculation

### Backend Functions ✅
- GPA/WMA calculation
- Grade assignment (A-E)
- Honors level determination
- Projection engine for target GPAs
- Transcript generation

### Frontend Pages ✅
- Login page
- Dashboard
- (Other pages templates ready)

### Admin Interface ✅
- Full Django admin integration
- Student management
- Grade management
- Customized admin views

---

## 🛠️ Common Tasks

### Create Superuser (First-time setup)
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
# Then login at http://localhost:8000/admin/
```

### Add a New Student via Admin Panel
1. Go to http://localhost:8000/admin/
2. Click "Students" in accounts section
3. Click "Add Student"
4. Fill in the form:
   - Select or create a User first
   - Enter registration number
   - Enter course name
   - Select year of study
   - Enter academic year
5. Click Save

### Add a New Student via Shell
```bash
python manage.py shell
```

```python
from accounts.models import Student
from django.contrib.auth.models import User

# Create a Django user account
user = User.objects.create_user(
    username='newstudent',
    email='newstudent@jkuat.ac.ke',
    password='password123',
    first_name='Jane',
    last_name='Doe'
)

# Create the student profile
student = Student.objects.create(
    user=user,
    registration_number='SCT211-0005/2021',
    course='Bachelor of Science in Computer Science',
    year_of_study=2,
    academic_year='2024/2025'
)

print(f"Created: {student.registration_number}")
exit()
```

### Add Grades for a Student
```bash
python manage.py shell
```

```python
from academics.models import Unit, Result
from accounts.models import Student

student = Student.objects.get(registration_number='SCT211-0005/2021')
unit = Unit.objects.get(code='MIT201')

result = Result.objects.create(
    student=student,
    unit=unit,
    score=85
)
# Auto-calculates grade and points!

exit()
```

### Calculate Student GPA
```bash
python manage.py shell
```

```python
from accounts.models import Student
from academics.utils import GradeCalculator

student = Student.objects.get(registration_number='SCT211-0001/2021')
gpa_data = GradeCalculator.calculate_wma(student)

print(f"GPA: {gpa_data['gpa']}")
print(f"Honors: {gpa_data['honors_level']}")
print(f"Units: {gpa_data['units_completed']}")

exit()
```

---

## 📝 File Locations

| File | Purpose |
|------|---------|
| `jkuat_gpa/settings.py` | Django configuration |
| `jkuat_gpa/urls.py` | URL routing |
| `academics/utils.py` | GPA calculation logic |
| `accounts/views.py` | Login/authentication |
| `templates/base.html` | Base page template |
| `.env` | Environment variables |
| `db.sqlite3` | Development database |

---

## ✨ Design Features

- 🎨 JKUAT Green (#4CAF50) color scheme
- 📱 Fully responsive Bootstrap 5 layout
- 🎯 Professional card-based UI
- 📊 Chart.js visualizations
- ⌨️ Keyboard navigation support
- 🔐 Secure authentication

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py shell < seed_data.py
```

### Login Not Working
- Verify registration number spelling
- Check password is `password123`
- Ensure student exists: `python manage.py shell`
- Run: `Student.objects.all()` to see all students

---

## 📞 Support

For issues or help:
1. Check `DEVELOPMENT.md` for detailed guides
2. Review `README.md` for full documentation
3. Check `COMPLETION_SUMMARY.md` for project status

---

## 🎯 Next Steps

### Phase 4 (UI Completion)
- [ ] Complete Transcript page
- [ ] Complete Units page
- [ ] Complete Projection page
- [ ] Complete Profile page

### Phase 5 (Advanced Features)
- [ ] Graduation planner UI
- [ ] PDF transcript export
- [ ] AI recommendations

### Phase 6 (Production)
- [ ] Unit tests
- [ ] Deploy to Render/Heroku
- [ ] Configure PostgreSQL

---

**Status**: Production-ready for testing  
**Last Updated**: December 18, 2024  
**Version**: 1.0  

Enjoy the GPA Calculator! 🎓
