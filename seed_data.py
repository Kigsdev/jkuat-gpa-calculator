"""
Sample data creation script for JKUAT GPA Calculator
Run with: python manage.py shell < seed_data.py
"""

from django.contrib.auth.models import User
from accounts.models import Student
from academics.models import AcademicYear, Unit, Result
import random

print("🌱 Starting database seeding...")

# Create academic year
ay, created = AcademicYear.objects.get_or_create(
    year=2024,
    semester=1,
    defaults={'is_active': True}
)
print(f"✅ Academic Year: {ay} (Created: {created})")

# Create units
units_data = [
    {'code': 'MIT201', 'name': 'Data Structures', 'credit_units': 3},
    {'code': 'MIT202', 'name': 'Web Development', 'credit_units': 4},
    {'code': 'MIT203', 'name': 'Database Systems', 'credit_units': 4},
    {'code': 'MIT204', 'name': 'Software Engineering', 'credit_units': 3},
    {'code': 'MIT205', 'name': 'Network Security', 'credit_units': 3},
    {'code': 'MIT206', 'name': 'Mobile Development', 'credit_units': 4},
]

units = []
for unit_data in units_data:
    unit, created = Unit.objects.get_or_create(
        code=unit_data['code'],
        academic_year=ay,
        defaults={
            'name': unit_data['name'],
            'credit_units': unit_data['credit_units']
        }
    )
    units.append(unit)
    status = "✅ Created" if created else "⏭️  Already exists"
    print(f"{status}: {unit.code} - {unit.name}")

# Create sample students with grades
sample_students = [
    {
        'username': 'student1',
        'email': 'student1@jkuat.ac.ke',
        'first_name': 'John',
        'last_name': 'Njogu',
        'registration': 'SCT211-0001/2021',
        'course': 'Bachelor of Science in Computer Science',
        'year': 2,
        'scores': [85, 78, 92, 88, 76, 84],
    },
    {
        'username': 'student2',
        'email': 'student2@jkuat.ac.ke',
        'first_name': 'Roy',
        'last_name': 'Kipchoge',
        'registration': 'SCT211-0002/2021',
        'course': 'Bachelor of Science in Computer Science',
        'year': 2,
        'scores': [72, 68, 75, 71, 69, 70],
    },
    {
        'username': 'student3',
        'email': 'student3@jkuat.ac.ke',
        'first_name': 'Vivian',
        'last_name': 'Muthoni',
        'registration': 'SCT211-0003/2021',
        'course': 'Bachelor of Science in Computer Science',
        'year': 2,
        'scores': [95, 92, 98, 94, 91, 96],
    },
    {
        'username': 'student4',
        'email': 'student4@jkuat.ac.ke',
        'first_name': 'Apphie',
        'last_name': 'Kimani',
        'registration': 'SCT211-0004/2021',
        'course': 'Bachelor of Science in Computer Science',
        'year': 2,
        'scores': [45, 52, 48, 55, 50, 46],
    },
]

print("\n" + "="*50)
print("👥 Creating Sample Students and Grades")
print("="*50)

for student_data in sample_students:
    # Create or get user
    user, user_created = User.objects.get_or_create(
        username=student_data['username'],
        defaults={
            'email': student_data['email'],
            'first_name': student_data['first_name'],
            'last_name': student_data['last_name'],
        }
    )
    
    # Set password for test user
    if user_created:
        user.set_password('password123')
        user.save()
    
    # Create or get student
    student, student_created = Student.objects.get_or_create(
        registration_number=student_data['registration'],
        defaults={
            'user': user,
            'course': student_data['course'],
            'year_of_study': student_data['year'],
            'academic_year': '2024/2025',
        }
    )
    
    status = "✅ Created" if student_created else "⏭️  Already exists"
    print(f"\n{status}: {student.registration_number}")
    print(f"   Name: {student.user.get_full_name()}")
    print(f"   Course: {student.course}")
    
    # Add grades
    for i, score in enumerate(student_data['scores']):
        result, result_created = Result.objects.get_or_create(
            student=student,
            unit=units[i],
            defaults={'score': score}
        )
        if result_created:
            print(f"   • {units[i].code}: {score}% → Grade {result.grade}")

print("\n" + "="*50)
print("✨ Database seeding complete!")
print("="*50)
print("\n🔐 Test Login Credentials:")
for student_data in sample_students:
    print(f"   Registration: {student_data['registration']} | Password: password123")

print("\n📊 Statistics:")
print(f"   Total Students: {Student.objects.count()}")
print(f"   Total Units: {Unit.objects.count()}")
print(f"   Total Results: {Result.objects.count()}")

# Show GPA calculations
print("\n📈 Student GPA Summary:")
from academics.utils import GradeCalculator
for student in Student.objects.all():
    gpa_data = GradeCalculator.calculate_wma(student)
    print(f"   {student.registration_number}: {gpa_data['gpa']} - {gpa_data['honors_level']}")
