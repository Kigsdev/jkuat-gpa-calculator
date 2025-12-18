from django.test import TestCase
from django.contrib.auth.models import User

from accounts.models import Student
from .models import AcademicYear, Unit, Result
from .utils import GradeCalculator


class GradeCalculatorTests(TestCase):
	def setUp(self):
		# Create user and student
		self.user = User.objects.create_user(username='teststudent', password='password')
		self.student = Student.objects.create(
			user=self.user,
			registration_number='SCT999-0001/2025',
			course='Test Course',
			year_of_study=2,
			academic_year='2024/2025'
		)

		# Academic year and units
		self.ay = AcademicYear.objects.create(year=2024, semester=1, is_active=True)
		self.u1 = Unit.objects.create(code='TST101', name='Test 1', credit_units=3, academic_year=self.ay)
		self.u2 = Unit.objects.create(code='TST102', name='Test 2', credit_units=4, academic_year=self.ay)
		self.u3 = Unit.objects.create(code='TST103', name='Test 3', credit_units=4, academic_year=self.ay)

		# Add results
		Result.objects.create(student=self.student, unit=self.u1, score=80)
		Result.objects.create(student=self.student, unit=self.u2, score=70)
		Result.objects.create(student=self.student, unit=self.u3, score=60)

	def test_get_grade_boundaries(self):
		# Boundary checks
		self.assertEqual(GradeCalculator.get_grade(70)[0], 'A')
		self.assertEqual(GradeCalculator.get_grade(69)[0], 'B')
		self.assertEqual(GradeCalculator.get_grade(60)[0], 'B')
		self.assertEqual(GradeCalculator.get_grade(59)[0], 'C')
		self.assertEqual(GradeCalculator.get_grade(50)[0], 'C')
		self.assertEqual(GradeCalculator.get_grade(49)[0], 'D')
		self.assertEqual(GradeCalculator.get_grade(40)[0], 'D')
		self.assertEqual(GradeCalculator.get_grade(39)[0], 'E')

	def test_calculate_wma(self):
		# Calculate expected weighted mean average
		total_points = 80 * 3 + 70 * 4 + 60 * 4
		total_credits = 3 + 4 + 4
		expected_gpa = round(total_points / total_credits, 2)

		gpa_data = GradeCalculator.calculate_wma(self.student)
		self.assertAlmostEqual(gpa_data['gpa'], float(expected_gpa), places=2)
		self.assertEqual(gpa_data['total_credit_units'], total_credits)
		self.assertEqual(gpa_data['units_completed'], 3)

	def test_project_required_average_simple(self):
		# If remaining units are 2, verify required average calculation is numeric and in range
		projection = GradeCalculator.project_required_average(self.student, target_gpa=70, remaining_units=2)
		self.assertIn('required_average', projection)
		self.assertIsInstance(projection['required_average'], float)
		self.assertGreaterEqual(projection['required_average'], 0.0)
		self.assertLessEqual(projection['required_average'], 100.0)

