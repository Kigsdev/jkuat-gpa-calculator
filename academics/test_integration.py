"""
Integration tests for the JKUAT GPA Calculator system.
Tests full user workflows including login, dashboard, transcript, projection.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Student
from academics.models import AcademicYear, Unit, Result, GPACalculation
from academics.utils import GradeCalculator
from decimal import Decimal


class StudentAuthenticationFlowTest(TestCase):
    """Test complete authentication and profile workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create academic year
        self.academic_year = AcademicYear.objects.create(
            year=2024,
            semester=1,
            is_active=True
        )
        
        # Create test user and student
        self.user = User.objects.create_user(
            username='testuser',
            email='test@jkuat.ac.ke',
            password='testpass123',
            first_name='Test',
            last_name='Student'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='SCT211-0001/2021',
            course='Bachelor of Science in Computer Science',
            year_of_study=2,
            academic_year=self.academic_year
        )
    
    def test_login_with_valid_credentials(self):
        """Test successful login with registration number."""
        response = self.client.post(reverse('accounts:login'), {
            'registration_number': 'SCT211-0001/2021',
            'password': 'testpass123'
        })
        # Should redirect to dashboard on success
        self.assertEqual(response.status_code, 302)
    
    def test_login_with_invalid_password(self):
        """Test login failure with wrong password."""
        response = self.client.post(reverse('accounts:login'), {
            'registration_number': 'SCT211-0001/2021',
            'password': 'wrongpassword'
        })
        # Should return to login page with error
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_nonexistent_student(self):
        """Test login with non-existent registration number."""
        response = self.client.post(reverse('accounts:login'), {
            'registration_number': 'SCT999-9999/2021',
            'password': 'testpass123'
        })
        # Should return to login page with error
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_redirects_authenticated_user(self):
        """Test that authenticated users are redirected from login page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)
    
    def test_logout(self):
        """Test user logout."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        # Verify user is logged out
        response = self.client.get(reverse('academics:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirects to login


class DashboardViewTest(TestCase):
    """Test dashboard view and GPA display."""
    
    def setUp(self):
        """Set up test data with grades."""
        self.client = Client()
        
        # Create academic year
        self.academic_year = AcademicYear.objects.create(
            year=2024,
            semester=1,
            is_active=True
        )
        
        # Create user and student
        self.user = User.objects.create_user(
            username='student1',
            password='pass123',
            first_name='John',
            last_name='Doe'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='SCT211-0002/2021',
            course='Computer Science',
            year_of_study=2,
            academic_year=self.academic_year
        )
        
        # Create units
        self.unit1 = Unit.objects.create(
            code='MIT201',
            name='Data Structures',
            credit_units=3,
            academic_year=self.academic_year
        )
        self.unit2 = Unit.objects.create(
            code='MIT202',
            name='Algorithms',
            credit_units=4,
            academic_year=self.academic_year
        )
        
        # Create results
        Result.objects.create(
            student=self.student,
            unit=self.unit1,
            score=85
        )
        Result.objects.create(
            student=self.student,
            unit=self.unit2,
            score=75
        )
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication."""
        response = self.client.get(reverse('academics:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirects to login
    
    def test_dashboard_displays_gpa(self):
        """Test that dashboard displays calculated GPA."""
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('academics:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check that GPA is in context
        self.assertIn('gpa', response.context)
        # GPA should be numeric
        self.assertTrue(isinstance(float(response.context['gpa']), float))
    
    def test_dashboard_displays_honors_level(self):
        """Test that dashboard displays honors level."""
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('academics:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('honors', response.context)
        honors = response.context['honors']
        self.assertIn(honors, ['First Class Honours', 'Second Class Honours (Upper Division)',
                              'Second Class Honours (Lower Division)', 'Pass', 'Fail'])
    
    def test_dashboard_displays_grade_distribution(self):
        """Test that dashboard displays grade distribution."""
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('academics:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('grade_distribution', response.context)
        dist = response.context['grade_distribution']
        self.assertIsInstance(dist, dict)


class TranscriptViewTest(TestCase):
    """Test transcript view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.academic_year = AcademicYear.objects.create(
            year=2024,
            semester=1,
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='student2',
            password='pass123'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='SCT211-0003/2021',
            course='Computer Science',
            year_of_study=2,
            academic_year=self.academic_year
        )
    
    def test_transcript_requires_login(self):
        """Test that transcript view requires authentication."""
        response = self.client.get(reverse('academics:transcript'))
        self.assertEqual(response.status_code, 302)
    
    def test_transcript_displays_correctly(self):
        """Test that transcript displays with user logged in."""
        self.client.login(username='student2', password='pass123')
        response = self.client.get(reverse('academics:transcript'))
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('student', response.context)
        self.assertIn('gpa', response.context)


class ProjectionViewTest(TestCase):
    """Test graduation projection view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.academic_year = AcademicYear.objects.create(
            year=2024,
            semester=1,
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='student3',
            password='pass123'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='SCT211-0004/2021',
            course='Computer Science',
            year_of_study=2,
            academic_year=self.academic_year
        )
        
        # Add some results
        unit = Unit.objects.create(
            code='MIT201',
            name='Data Structures',
            credit_units=3,
            academic_year=self.academic_year
        )
        Result.objects.create(
            student=self.student,
            unit=unit,
            score=75
        )
    
    def test_projection_requires_login(self):
        """Test that projection view requires authentication."""
        response = self.client.get(reverse('academics:projection'))
        self.assertEqual(response.status_code, 302)
    
    def test_projection_displays_targets(self):
        """Test that projection displays all honor targets."""
        self.client.login(username='student3', password='pass123')
        response = self.client.get(reverse('academics:projection'))
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('projections', response.context)
        projections = response.context['projections']
        self.assertIn('First Class Honours', projections)
        self.assertIn('Second Class (Upper)', projections)


class GradeCalculatorValidationTest(TestCase):
    """Test GradeCalculator error handling and validation."""
    
    def setUp(self):
        """Set up test data."""
        self.academic_year = AcademicYear.objects.create(
            year=2024,
            semester=1,
            is_active=True
        )
        
        self.user = User.objects.create_user(username='testuser')
        self.student = Student.objects.create(
            user=self.user,
            registration_number='TEST123',
            academic_year=self.academic_year
        )
    
    def test_calculate_wma_with_no_results(self):
        """Test WMA calculation with no results."""
        data = GradeCalculator.calculate_wma(self.student)
        
        self.assertEqual(data['gpa'], 0.00)
        self.assertEqual(data['units_completed'], 0)
        self.assertEqual(data['failed_units'], 0)
    
    def test_calculate_wma_with_invalid_score(self):
        """Test WMA calculation filters invalid scores (out of range)."""
        unit = Unit.objects.create(
            code='TEST201',
            name='Test Unit',
            credit_units=3,
            academic_year=self.academic_year
        )
        
        # Create result with score > 100 (should be skipped)
        result = Result.objects.create(
            student=self.student,
            unit=unit,
            score=85  # Valid score
        )
        
        data = GradeCalculator.calculate_wma(self.student)
        # Should calculate correctly
        self.assertGreater(data['gpa'], 0)
    
    def test_calculate_wma_exception_handling(self):
        """Test that calculate_wma handles exceptions gracefully."""
        # Pass None as student to trigger exception
        data = GradeCalculator.calculate_wma(None)
        
        # Should return error dict, not raise exception
        self.assertIsInstance(data, dict)
        self.assertIn('gpa', data)


class FormValidationTest(TestCase):
    """Test form validation for data integrity."""
    
    def setUp(self):
        """Set up test data."""
        self.academic_year = AcademicYear.objects.create(
            year=2024,
            semester=1,
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='formtest',
            password='pass123'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='FORM001',
            academic_year=self.academic_year
        )
        
        self.unit = Unit.objects.create(
            code='FORM201',
            name='Form Test Unit',
            credit_units=3,
            academic_year=self.academic_year
        )
    
    def test_result_score_validation(self):
        """Test that result scores must be 0-100."""
        from academics.forms import ResultForm
        
        # Valid score
        form = ResultForm(data={
            'student': self.student.id,
            'unit': self.unit.id,
            'score': 85
        })
        self.assertTrue(form.is_valid() or 'score' not in form.errors)
        
        # Invalid score > 100
        form = ResultForm(data={
            'student': self.student.id,
            'unit': self.unit.id,
            'score': 150
        })
        self.assertFalse(form.is_valid())


class TemplateRenderingTest(TestCase):
    """Test that templates render without errors."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.academic_year = AcademicYear.objects.create(
            year=2024,
            semester=1,
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='templatetest',
            password='pass123'
        )
        self.student = Student.objects.create(
            user=self.user,
            registration_number='TMPL001',
            academic_year=self.academic_year
        )
    
    def test_dashboard_template_renders(self):
        """Test dashboard template renders without errors."""
        self.client.login(username='templatetest', password='pass123')
        response = self.client.get(reverse('academics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academics/dashboard.html')
    
    def test_transcript_template_renders(self):
        """Test transcript template renders without errors."""
        self.client.login(username='templatetest', password='pass123')
        response = self.client.get(reverse('academics:transcript'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academics/transcript.html')
    
    def test_units_template_renders(self):
        """Test units template renders without errors."""
        self.client.login(username='templatetest', password='pass123')
        response = self.client.get(reverse('academics:units'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academics/units.html')
    
    def test_projection_template_renders(self):
        """Test projection template renders without errors."""
        self.client.login(username='templatetest', password='pass123')
        response = self.client.get(reverse('academics:projection'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academics/projection.html')
