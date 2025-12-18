# JKUAT GPA Calculation & Graduation Planner

A secure, user-friendly academic tracking system for JKUAT students to calculate current GPA, project future grades, and receive AI-driven academic advice.

## 🎯 Project Overview

This application helps students:
- Calculate current GPA based on JKUAT grading standards
- Project future grades needed for specific honors (First Class, Second Class, etc.)
- Track academic progress and performance metrics
- Plan for graduation with target achievements

## 🏗️ Project Structure

```
jkuat_gpa/
├── academics/              # Academic logic and models
│   ├── models.py          # AcademicYear, Unit, Result, GPACalculation
│   ├── views.py           # Academic-related views
│   ├── forms.py           # Forms for grade entry
│   └── urls.py            # Academic app URLs
├── accounts/              # User authentication
│   ├── models.py          # Student (extended User)
│   ├── views.py           # Login, Logout, Registration
│   ├── forms.py           # Authentication forms
│   └── urls.py            # Auth URLs
├── jkuat_gpa/
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Main URL router
│   └── wsgi.py            # WSGI application
├── templates/             # HTML templates
├── static/                # CSS, JS, Images
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

## 🔧 Technology Stack

- **Language**: Python 3.12
- **Framework**: Django 4.2.7
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: 
  - Development: SQLite
  - Production: PostgreSQL
- **Authentication**: Django built-in auth system
- **ORM**: Django ORM

## 📋 Database Models

### Student
- Extends Django's User model
- Registration Number (unique identifier for login)
- Course name
- Year of study
- Academic year

### AcademicYear
- Year and semester tracking
- Active status
- Links to all units in that period

### Unit
- Unit code and name
- Credit factors (1-4 typically)
- Associated academic year

### Result
- Student score for a unit (0-100)
- Auto-calculated grade (A-E)
- Auto-calculated weighted points
- Unique per student-unit combination

### GPACalculation
- Cached GPA/WMA per student per academic year
- Total points and credit units
- Historical tracking

## 📊 Grading Standards

| Grade | Score Range | Honors Level |
|-------|-------------|--------------|
| A | 70-100% | First Class Honours |
| B | 60-69% | Second Class Honours (Upper) |
| C | 50-59% | Second Class Honours (Lower) |
| D | 40-49% | Pass |
| E | 0-39% | Fail |

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Virtual environment (venv)

### Installation

1. **Clone the repository**
```bash
cd /path/to/project
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (admin)**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

## 📱 Features

### Phase 1: Project Setup ✅
- Django project initialized
- Git repository configured
- Virtual environment setup
- Requirements documented

### Phase 2: Database Architecture ✅
- Student model with registration number
- Academic year tracking
- Unit management
- Result storage with auto-grading
- GPA calculation caching

### Phase 3: Backend Logic (In Progress)
- [ ] Grading utility functions
- [ ] GPA/WMA calculation engine
- [ ] Projection engine for future targets

### Phase 4: UI/UX Design
- [ ] Login page with JKUAT branding
- [ ] Dashboard with current stats
- [ ] Responsive Bootstrap layout

### Phase 5: Advanced Features
- [ ] Graduation planner
- [ ] AI-driven academic advice
- [ ] Transcript generation

### Phase 6: Testing & Deployment
- [ ] Unit tests
- [ ] Integration tests
- [ ] Production deployment

## 🔐 Security Features

- Django's built-in authentication system
- CSRF protection
- SQL injection prevention via ORM
- Password validation
- Secure session management
- Environment-based configuration

## 👥 Team Members

- Roy
- John Njogu
- Vivian
- Apphie
- John Kigotho

## 📄 License

Developed for JKUAT Educational Purposes

## 📞 Support

For issues or questions, contact your development lead.

---

**Last Updated**: December 18, 2024  
**Status**: Phase 2 Complete - Ready for Phase 3
