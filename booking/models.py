from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class SystemUser(AbstractUser):
    class Meta:
        verbose_name_plural = '管理ユーザー'
    REGISTER = 'register'
    ADMIN = 'admin'
    DISPLAY = 'display'

    TYPE_OPTION = [
        (REGISTER, _('登録端末')),
        (ADMIN, _('管理者')),
        (DISPLAY, _('表示端末 (iPadなど)')), 
    ]

    type = models.CharField(        
        verbose_name='アカウントの種類',
        max_length=8,
        choices = TYPE_OPTION,
    )

#Students Class
class Student(models.Model):
    class Meta:
        verbose_name_plural = '生徒アカウント'

    #Homeroom Grade Options
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    OTHER = "OTHER"

    HR_GRADE_OPTION = [
        (M1, _('M1')),
        (M2, _('M2')),
        (M3, _('M3')),
        (H1, _('H1')),
        (H2, _('H2')),
        (H3, _('H3')),
    ]

    student_id = models.CharField(verbose_name='学籍番号', max_length=7, unique=True)

    last_name = models.CharField(verbose_name='姓', max_length=100)
    first_name = models.CharField(verbose_name='名', max_length=100)

    hr_grade = models.CharField(
        verbose_name='学年',
        max_length = 5,
        choices = HR_GRADE_OPTION,
    )
    hr_class = models.IntegerField(verbose_name='組', null=True, blank=True)
    student_num = models.IntegerField(verbose_name='出席番号', null=True, blank=True)
 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['student_id']

    def __str__(self):
        return self.full_hr_class() + " " + self.full_name()
    

    def full_name(self):
        """
        Return string full name.
        Grade: H1, Class: 6 -> "H1-6"
        """
        return self.last_name + self.first_name

    def full_hr_class(self):
        """
        Return string grade class.
        Grade: H1, Class: 6 -> "H1-6"
        """
        return str(self.hr_grade) + "-" + str(self.hr_class)

    def full_hr_class_and_num(self):
        """
        Return string grade class and student number.
        Grade: H1, Class: 6 Student #: 24-> "H1-6 #24"
        """
        return self.full_hr_class() + " #" +  str(self.student_num)


class Seat(models.Model):
    AVAILABLE = 0
    USED = 1
    RESERVED = 2
    UNAVAILABLE = 9

    STATUS = [
        (AVAILABLE, _('空席')),
        (USED, _('使用中')),
        (RESERVED, _('予約')),
        (UNAVAILABLE, _('使用不可')),
    ]

    seat_id = models.IntegerField(verbose_name='座席番号')
    status = models.IntegerField(
        verbose_name='ステータス',
        choices = STATUS,
        default = AVAILABLE,
    )
    internet = models.BooleanField(verbose_name='インターネット利用')
    current_user = models.OneToOneField("Student", 
                                        verbose_name=("利用者"), 
                                        on_delete=models.CASCADE, 
                                        null=True, blank=True)
    guest_user = models.BooleanField(verbose_name='ゲスト', default=False)


class Log(models.Model):
    seat_id = models.IntegerField(verbose_name='座席番号')
    user = models.ForeignKey("Student", 
                                        verbose_name=("利用者"), 
                                        on_delete=models.CASCADE, 
                                        null=True, blank=True)
    guest_user = models.BooleanField(verbose_name='ゲスト', default=False)
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    