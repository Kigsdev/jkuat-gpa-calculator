# JKUAT GPA Calculator - API & Architecture Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Database Models](#database-models)
3. [Views & URL Routing](#views--url-routing)
4. [Forms & Validation](#forms--validation)
5. [Utility Functions](#utility-functions)
6. [Templates](#templates)
7. [Error Handling](#error-handling)
8. [Testing](#testing)

---

## System Architecture

### Tech Stack
- **Framework**: Django 4.2.7
- **Python**: 3.12
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: Bootstrap 5.3, Chart.js
- **Authentication**: Django built-in auth with custom Student profile

### Architecture Pattern: MVT (Model-View-Template)

```
┌─────────────────────────────────────────────────────────┐
│                    Django Project                        │
├─────────────────────────────────────────────────────────┤
│  Django Admin │  Templates (HTML)  │  Static (CSS/JS)   │
└────────┬──────────────┬──────────────────┬──────────────┘
         │              │                  │
      [URLs]      [Views/Context]    [Bootstrap/Charts]
         │              │                  │
┌────────▼──────────────▼──────────────────▼──────────────┐
│              Application Layer (Business Logic)          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  GradeCalculator Utility (academics/utils.py)   │  │
│  │  - calculate_wma()                               │  │
│  │  - get_grade()                                   │  │
│  │  - get_transcript()                              │  │
│  │  - project_required_average()                    │  │
│  └──────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────┐
│           Data Models (Django ORM)                        │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │   Student    │  │ AcademicYear  │  │    Unit      │  │
│  │ (User Ext.)  │  │  (year, sem)  │  │  (code,cr)   │  │
│  └──────────────┘  └───────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌───────────────────────────────┐   │
│  │   Result     │  │   GPACalculation (cache)      │   │
│  │ (grade calc) │  │                               │   │
│  └──────────────┘  └───────────────────────────────┘   │
└────────┬──────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────┐
│              Database Layer                                │
│  Tables: auth_user, accounts_student, academics_*         │
└───────────────────────────────────────────────────────────┘
```

---

## Database Models

### 1. Student Model
**Location**: `accounts/models.py`
**Purpose**: Extend Django User with student profile

```python
class Student(models.Model):
    user = OneToOneField(User)
    registration_number = CharField(unique=True)  # SCT211-0001/2021
    course = CharField()
    year_of_study = IntegerField()
    academic_year = ForeignKey(AcademicYear)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Key Fields**:
- `registration_number`: Unique identifier used for login (e.g., SCT211-0001/2021)
- `course`: Bachelor program name
- `year_of_study`: Current academic year (1-4)
- `academic_year`: Current active academic year

**Relationships**:
- OneToOne: User (Django auth)
- ForeignKey: AcademicYear

---

### 2. AcademicYear Model
**Location**: `academics/models.py`
**Purpose**: Represent academic sessions and semesters

```python
class AcademicYear(models.Model):
    year = IntegerField()                    # 2024
    semester = IntegerField(choices=[(1, 'Semester 1'), (2, 'Semester 2')])
    is_active = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

**Key Fields**:
- `year`: Academic year start (e.g., 2024 for 2024/2025)
- `semester`: Which semester (1 or 2)
- `is_active`: Current active semester for dashboard

**Unique Constraint**: `(year, semester)` - Only one entry per semester

**String Representation**: `"2024/2025 - Semester 1"`

---

### 3. Unit Model
**Location**: `academics/models.py`
**Purpose**: Store course units with credit weighting

```python
class Unit(models.Model):
    code = CharField(unique=True)            # MIT201
    name = CharField()                       # Data Structures
    credit_units = IntegerField()            # 3-4
    academic_year = ForeignKey(AcademicYear)
    created_at = DateTimeField(auto_now_add=True)
```

**Key Fields**:
- `code`: Unit identifier (e.g., MIT201)
- `name`: Full unit name
- `credit_units`: Credit weighting for GPA (typically 3-4)
- `academic_year`: Which academic year this unit runs

**Relationships**:
- ForeignKey: AcademicYear

---

### 4. Result Model
**Location**: `academics/models.py`
**Purpose**: Store grades and calculate GPA contributions

```python
class Result(models.Model):
    student = ForeignKey(Student)
    unit = ForeignKey(Unit)
    score = IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    grade = CharField(max_length=1, choices=[('A', 'A'), ... ('E', 'E')])
    points = DecimalField()
    created_at = DateTimeField(auto_now_add=True)
```

**Key Fields**:
- `score`: Raw score 0-100
- `grade`: Calculated letter grade (A-E)
- `points`: score × credit_units (calculated on save)

**Auto-Calculation in save()**:
```python
# Grade assignment
70-100: A
60-69:  B
50-59:  C
40-49:  D
0-39:   E

# Points calculation
points = score × unit.credit_units
```

**Unique Constraint**: `(student, unit)` - One result per student per unit

**Relationships**:
- ForeignKey: Student
- ForeignKey: Unit

---

### 5. GPACalculation Model
**Location**: `academics/models.py`
**Purpose**: Cache calculated GPA for performance

```python
class GPACalculation(models.Model):
    student = ForeignKey(Student)
    academic_year = ForeignKey(AcademicYear)
    gpa = DecimalField()
    total_points = DecimalField()
    total_credit_units = IntegerField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Purpose**: Cache to avoid recalculating on every page load

---

## Views & URL Routing

### URL Structure

```
/                          → Landing page (TemplateView)
/accounts/
  ├─ login/               → LoginView (POST for auth)
  ├─ logout/              → LogoutView (GET)
  ├─ register/            → RegisterView (info page)
  └─ profile/             → StudentProfileView (GET)

/academics/
  ├─ dashboard/           → DashboardView (GET)
  ├─ transcript/          → TranscriptView (GET)
  ├─ units/               → UnitsView (GET)
  └─ projection/          → ProjectionView (GET)

/admin/                    → Django admin panel
```

### View Details

#### LoginView (accounts/views.py)
**Type**: Function-based View
**HTTP Methods**: GET, POST
**Authentication**: None (public)
**Purpose**: Handle student login with registration number

**GET**: Display login form
**POST**: Authenticate student
- Validates registration_number and password
- Looks up Student by registration_number
- Authenticates associated User
- Sets Django session
- Redirects to dashboard on success

**Error Handling**:
- Missing fields → "Field is required"
- Wrong password → "Invalid registration number or password"
- Student not found → "Student not found"

**Redirects**:
- Success → `academics:dashboard`
- Authenticated user → `academics:dashboard`

---

#### DashboardView (academics/views.py)
**Type**: Class-based View (TemplateView)
**HTTP Methods**: GET
**Authentication**: LoginRequiredMixin
**Template**: `academics/dashboard.html`

**Context Data**:
```python
{
    'student': Student object,
    'gpa': 83.95 (formatted string),
    'honors': 'First Class Honours',
    'units_completed': 6,
    'failed_units': 0,
    'total_points': 503.7,
    'total_credit_units': 6,
    'grade_distribution': {'A': 2, 'B': 3, 'C': 1, 'D': 0, 'E': 0}
}
```

**Data Calculation**:
- Calls `GradeCalculator.calculate_wma(student)`
- Calls `GradeCalculator.get_grade_distribution(student)`

**Error Handling**:
- Student profile missing → Shows error message
- Database error → Shows error message with exception details

---

#### TranscriptView (academics/views.py)
**Type**: Class-based View (TemplateView)
**HTTP Methods**: GET
**Authentication**: LoginRequiredMixin
**Template**: `academics/transcript.html`

**Context Data**:
```python
{
    'student': Student object,
    'transcript': [
        {
            'code': 'MIT201',
            'name': 'Data Structures',
            'score': 85,
            'grade': 'A',
            'points': 255,
            'credit_units': 3,
            'honors_level': 'First Class Honours'
        },
        ...
    ],
    'gpa': 83.95,
    'total_points': 503.7,
    'honors_level': 'First Class Honours'
}
```

**Data Source**: `GradeCalculator.get_transcript(student)`

---

#### UnitsView (academics/views.py)
**Type**: Class-based View (TemplateView)
**HTTP Methods**: GET
**Authentication**: LoginRequiredMixin
**Template**: `academics/units.html`

**Context Data**:
```python
{
    'student': Student object,
    'results': QuerySet[Result],  # Ordered by unit code
    'total_units': 6
}
```

**Query Optimization**:
```python
Result.objects.filter(student=student)
       .select_related('unit')
       .order_by('unit__code')
```

---

#### ProjectionView (academics/views.py)
**Type**: Class-based View (TemplateView)
**HTTP Methods**: GET
**Authentication**: LoginRequiredMixin
**Template**: `academics/projection.html`

**Context Data**:
```python
{
    'student': Student object,
    'current_gpa': 83.95,
    'honors_level': 'First Class Honours',
    'remaining_units': 8,
    'projections': {
        'First Class Honours': {
            'required_average': 78.5,
            'is_achievable': True,
            'message': 'Achievable: target X% average'
        },
        'Second Class (Upper)': {...},
        'Second Class (Lower)': {...},
        'Pass': {...}
    }
}
```

**Projection Calculation**:
```python
for target_gpa in [70, 60, 50, 40]:
    projection = GradeCalculator.project_required_average(
        student,
        target_gpa,
        remaining_units=8
    )
```

---

## Forms & Validation

### LoginForm (accounts/forms.py)
```python
class LoginForm(Form):
    registration_number = CharField()
    password = CharField(widget=PasswordInput)
    
    def clean(self):
        # Validates both fields are present
```

### RegisterForm (accounts/forms.py)
```python
class RegisterForm(UserCreationForm):
    password1 = CharField(widget=PasswordInput)
    password2 = CharField(widget=PasswordInput)
    
    def clean(self):
        # Validates password1 == password2
    
    def save(self, commit=True):
        # Uses user.set_password() for hashing
```

### StudentProfileForm (accounts/forms.py)
```python
class StudentProfileForm(ModelForm):
    class Meta:
        model = Student
        fields = ['registration_number', 'course', 'year_of_study', 'academic_year']
    
    def clean_academic_year(self):
        # Format validation: YYYY/YYYY
    
    def clean_course(self):
        # Min length validation
```

### ResultForm (academics/forms.py)
```python
class ResultForm(ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'unit', 'score']
    
    def clean_score(self):
        # Validates 0 <= score <= 100
    
    def clean(self):
        # Validates student-unit uniqueness
```

### ProjectionForm (academics/forms.py)
```python
class ProjectionForm(Form):
    remaining_units = IntegerField(min_value=1, max_value=20)
    target_honors = ChoiceField(choices=[
        ('70', 'First Class Honours'),
        ('60', 'Second Class (Upper)'),
        ('50', 'Second Class (Lower)'),
        ('40', 'Pass')
    ])
    
    def clean_remaining_units(self):
        # Validates 1-20 units
    
    def clean_target_honors(self):
        # Validates selection is valid
```

---

## Utility Functions

### GradeCalculator (academics/utils.py)

#### get_grade(score: int) → Tuple[str, str]
```python
GradeCalculator.get_grade(85)
# Returns: ('A', 'First Class Honours')

# Grade boundaries (JKUAT standards)
70-100: A - First Class Honours
60-69:  B - Second Class Honours (Upper Division)
50-59:  C - Second Class Honours (Lower Division)
40-49:  D - Pass
0-39:   E - Fail
```

---

#### calculate_wma(student: Student, academic_year: AcademicYear = None) → Dict
```python
GradeCalculator.calculate_wma(student)
# Returns:
{
    'gpa': 83.95,
    'total_points': 503.7,
    'total_credit_units': 6,
    'units_completed': 6,
    'failed_units': 0,
    'honors_level': 'First Class Honours'
}
```

**Formula**: WMA = Σ(score × credit_units) / Σ(credit_units)

**Error Handling**:
- None scores are skipped
- Out-of-range scores are skipped
- Empty results → Returns zeros with 'No grades recorded yet'
- Exception → Returns zeros with error message

---

#### get_grade_distribution(student: Student) → Dict[str, int]
```python
GradeCalculator.get_grade_distribution(student)
# Returns:
{
    'A': 2,
    'B': 3,
    'C': 1,
    'D': 0,
    'E': 0
}
```

---

#### get_transcript(student: Student, academic_year: AcademicYear = None) → List[Dict]
```python
GradeCalculator.get_transcript(student)
# Returns:
[
    {
        'code': 'MIT201',
        'name': 'Data Structures',
        'score': 85,
        'grade': 'A',
        'credit_units': 3,
        'points': 255,
        'honors_level': 'First Class Honours'
    },
    ...
]
```

---

#### project_required_average(student: Student, target_gpa: float, remaining_units: int) → Dict
```python
GradeCalculator.project_required_average(student, 70.0, 8)
# Returns:
{
    'required_average': 78.5,
    'is_achievable': True,
    'message': 'You need an average of 78.5% in remaining units to achieve First Class Honours'
}
```

**Logic**:
- Calculate weighted contribution needed from remaining units
- Check if required average is within 0-100 range
- Return achievability assessment

---

## Templates

### Base Template: `templates/base.html`
- Bootstrap 5 responsive grid
- JKUAT green navbar (#4CAF50)
- Navigation sidebar (authenticated users)
- Message display for feedback
- Chart.js and Bootstrap JS loaded

**Key CSS Classes**:
- `.navbar-green`: JKUAT theme color
- `.stat-card`: Statistics display card with h-100 for consistency
- `.grade-a`, `.grade-b`, etc: Grade badge styling
- `.sidebar-nav`: Left navigation menu

---

### Dashboard: `templates/academics/dashboard.html`
- GPA display with honors badge
- Grade distribution doughnut chart (Chart.js)
- Statistics cards: units completed, failed units, points
- Quick action links to other pages

**JavaScript**:
- Chart.js initialization with null-safety check
- Dynamic data loading from context

---

### Transcript: `templates/academics/transcript.html`
- Table of all course units with scores and grades
- Grade-colored badges for visual identification
- Summary statistics: total GPA, total points, honors level
- Print-friendly formatting

---

### Units: `templates/academics/units.html`
- Card grid display of enrolled units
- Each card shows: unit code, name, score, grade, credit units, points
- Responsive layout (3-column on desktop, 1-column on mobile)

---

### Projection: `templates/academics/projection.html`
- Four honor level targets (70%, 60%, 50%, 40%)
- Required average calculation for each
- Achievability indicator with color coding
- Actionable messages

---

### Login: `templates/accounts/login.html`
- Registration number input field
- Password input field
- Error message display
- Help modal with login instructions

---

## Error Handling

### View Level
Each view has try-except block:
```python
try:
    student = self.request.user.student
    # ... calculations ...
except ObjectDoesNotExist:
    context['error'] = 'Student profile not found. Please contact the registrar.'
except Exception as e:
    context['error'] = f'Error loading dashboard: {str(e)}'
    print(f"Error: {str(e)}")  # Log for debugging
```

### Model Level
Result.save() validates:
- None scores are handled gracefully
- Invalid data doesn't break calculation
- Decimal precision is maintained

### Utility Level
GradeCalculator methods:
- Return default values on empty results
- Catch exceptions and return error dict
- Skip invalid records rather than crash

### Template Level
Templates use default filters:
```html
{{ gpa|default:"0.00" }}
{{ honors|default:"No grades recorded yet" }}
```

---

## Testing

### Test Files
1. **academics/tests.py** - 3 unit tests
   - `test_get_grade_boundaries`: Grade assignment correctness
   - `test_calculate_wma`: GPA calculation accuracy
   - `test_project_required_average_simple`: Projection logic

2. **academics/test_integration.py** - 21 integration tests
   - Authentication flows (5 tests)
   - Dashboard display (4 tests)
   - Transcript display (2 tests)
   - Projections (2 tests)
   - Validation (3 tests)
   - Forms (1 test)
   - Templates (4 tests)

### Test Coverage
- **Authentication**: Login, logout, redirect flows
- **Views**: Permission checks, context data, error handling
- **Database**: Model relationships, cascading deletes
- **Calculations**: GPA accuracy, grade boundaries
- **Forms**: Validation rules, password hashing
- **Templates**: Rendering without errors

### Running Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test academics

# Specific test class
python manage.py test academics.tests.GradeCalculatorTests

# With verbosity
python manage.py test academics --verbosity 2

# Current status: 24/24 tests passing ✅
```

---

## Performance Considerations

### Database Queries
- Use `select_related()` for ForeignKey relationships
- Use `prefetch_related()` for reverse relationships
- Index on `registration_number` for login queries

### Caching
- GPACalculation model caches computed values
- Consider adding Redis for multi-user scenarios

### Optimization
- Template rendering is lightweight
- Chart.js loads with async defer
- Static files should be minified in production

---

## Security

### Authentication
- Django's built-in password hashing (PBKDF2)
- Registration_number used instead of username
- LoginRequiredMixin on all academic views

### Form Validation
- CSRF protection on all POST requests
- Input validation on all form fields
- SQL injection prevention via Django ORM

### Data Protection
- Never expose passwords in templates
- Sensitive data only in authenticated views
- Error messages don't leak system info

---

## Deployment

### Environment Variables (.env)
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Database Migration
```bash
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

### WSGI Server (Gunicorn)
```bash
gunicorn jkuat_gpa.wsgi:application --bind 0.0.0.0:8000
```

---

## API Endpoints (Potential REST API)

Future enhancement: Add Django REST Framework for API endpoints:

```
GET /api/student/dashboard/        → Dashboard data JSON
GET /api/student/transcript/        → Transcript data JSON
GET /api/student/projection/        → Projection data JSON
POST /api/results/                  → Create grade entry
GET /api/units/                     → List enrolled units
```

---

## Troubleshooting

### Student Not Found on Login
- Verify `registration_number` matches database exactly
- Check case sensitivity (if applicable)
- Confirm Student linked to User

### GPA Shows 0.00
- Check Results exist for the student
- Verify scores are in 0-100 range
- Check AcademicYear is set for student

### Charts Not Displaying
- Check browser console for JS errors
- Verify Chart.js is loaded
- Check canvas element exists in DOM

### Forms Not Validating
- Check form clean() methods are called
- Verify error messages display in template
- Check form is bound with POST data

---

## Future Enhancements

1. **REST API**: Django REST Framework endpoints
2. **PDF Export**: Generate transcript PDFs
3. **Email Notifications**: Send grade updates
4. **Advanced Analytics**: Predict graduation honors
5. **Mobile App**: React Native frontend
6. **AI Recommendations**: Study recommendations based on trends
7. **Multi-language**: Internationalization (i18n)
8. **SSO Integration**: LDAP/Active Directory login
