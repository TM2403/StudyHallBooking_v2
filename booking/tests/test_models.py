from django.test import TestCase
from ..models import *

class StudentTests(TestCase):
    def setUp(self):
        Student.objects.create(student_id=7777777, 
                                last_name='田中', 
                                first_name='二郎', 
                                hr_grade='H3', 
                                hr_class=2,
                                student_num=29)
        
        Student.objects.create(student_id=8888888, 
                                last_name='Jackson', 
                                first_name='Kurt', 
                                hr_grade='M2', 
                                hr_class=7,
                                student_num=3)

    def test_full_name(self):
        japanese = Student.objects.get(student_id=7777777)
        english = Student.objects.get(student_id=8888888)
        self.assertEqual(japanese.full_name(), '田中二郎')
        self.assertEqual(english.full_name(), 'Kurt Jackson')

    def test_full_hr_class(self):
        japanese = Student.objects.get(student_id=7777777)
        english = Student.objects.get(student_id=8888888)
        self.assertEqual(japanese.full_hr_class(), 'H3-2')
        self.assertEqual(english.full_hr_class(), 'M2-7')

    def test_full_hr_class_and_num(self):
        japanese = Student.objects.get(student_id=7777777)
        english = Student.objects.get(student_id=8888888)
        self.assertEqual(japanese.full_hr_class_and_num(), 'H3-2 #29')
        self.assertEqual(english.full_hr_class_and_num(), 'M2-7 #3')        
                