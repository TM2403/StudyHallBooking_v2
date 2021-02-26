import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Seat, Student

class StudentEditForm(forms.Form):
    #Homeroom Grade Options
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    OTHER = "OTHER"

    HR_GRADE_OPTION = (
        (M1, 'M1'),
        (M2, 'M2'),
        (M3, 'M3'),
        (H1, 'H1'),
        (H2, 'H2'),
        (H3, 'H3'),
    )


    last_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': "form-control w-50 mx-auto"})
    )

    first_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'class': "form-control w-50 mx-auto"})
    )

    hr_grade = forms.ChoiceField(
        required=True,
        choices = HR_GRADE_OPTION,
        widget=forms.Select(attrs={'class': "form-control w-50 mx-auto"})
    )
    
    hr_class = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': "form-control w-50 mx-auto"}),
    )
    
    student_num = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': "form-control w-50 mx-auto"})
    )

    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)
        self.fields['hr_class'].validators.append(self.class_validator)
        self.fields['student_num'].validators.append(self.student_num_validator)

    def class_validator(self, value):
        if value > 9 or value < 1:
            raise ValidationError('クラスの入力に誤りがあります。Inappropriate class number.', code='illegal_class')

    def student_num_validator(self, value):
        if value > 40 or value < 1:
            raise ValidationError('出席番号の入力に誤りがあります。Inappropriate student number.', code='illegal_student_number')  




class StudentIDForm(forms.Form):
    student_id = forms.CharField(required=True, 
                                    max_length=7, 
                                    min_length=7,
                                    widget=forms.TextInput(attrs={'class': "form-control w-50", 'style': "margin-left: 25%", 'autofocus': "autofocus"}))

    def __init__(self, type, *args, **kwargs):
        super(StudentIDForm, self).__init__(*args, **kwargs)
        self.fields['student_id'].validators.append(self.student_id_validator)
        if type == 'check_in':
            self.fields['student_id'].validators.append(self.check_in_validator)
        elif type == 'check_out':
            self.fields['student_id'].validators.append(self.check_out_validator)

    def student_id_validator(self, value):
        check = re.fullmatch('\d{7}', value)
        if check is None:
            raise ValidationError('学籍番号は７桁の数字です。Stuent ID must be 7-digit number.', code='invalid_id')

    def check_in_validator(self, value):
        try:
            user = Student.objects.get(student_id=value)
            try:
                seat = Seat.objects.get(current_user=user)
                raise ValidationError('既に入室済みです。You are already checked in.', code='already_in')   
            except Seat.DoesNotExist:             
                pass

        except Student.DoesNotExist:
            pass
        #    raise ValidationError('アカウントが存在しません。Account does not exist.', code='no_account')
    
    def check_out_validator(self, value):
        try:
            user = Student.objects.get(student_id=value)
            try:
                seat = Seat.objects.get(current_user=user)  
            except Seat.DoesNotExist:             
                raise ValidationError('入室していません。You are not checked in.', code='already_out') 

        except Student.DoesNotExist:
            raise ValidationError('アカウントが存在しません。Account does not exist.', code='no_account')

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={
                'class': 'form-control w-50 loginform-content',
                'placeholder': 'ユーザーネーム', 
            }
        ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control w-50 loginform-content',
            'placeholder': 'パスワード', 
        }
    ))