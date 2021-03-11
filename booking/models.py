import re

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

#管理ユーザーモデル
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

#生徒アカウントのモデル
class Student(models.Model):
    class Meta:
        verbose_name_plural = '生徒アカウント'

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

    REQUIRED_FIELDS = ['student_id']

    def __str__(self):
        return self.full_hr_class() + " " + self.full_name()

    def full_name(self):
        check_last_name = re.fullmatch('^[a-zA-Z]+$', self.last_name)
        check_first_name = re.fullmatch('^[a-zA-Z]+$', self.first_name)
        
        if check_first_name is None and check_last_name is None:
            return self.last_name + self.first_name
        else:
            return self.first_name + " " + self.last_name

    def full_hr_class(self):
        return str(self.hr_grade) + "-" + str(self.hr_class)

    def full_hr_class_and_num(self):
        return self.full_hr_class() + " #" +  str(self.student_num)

#座席のモデル
class Seat(models.Model):
    AVAILABLE = 0
    TAKEN = 1    
    RESERVED = 2   #試験導入　将来検討してもいいかも
    UNAVAILABLE = 9

    STATUS = [
        (AVAILABLE, _('空席')),
        (TAKEN, _('使用中')),
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


#入退室記録のモデル
class Log(models.Model):
    seat_id = models.IntegerField(verbose_name='座席番号')
    user = models.ForeignKey("Student", 
                                        verbose_name=("利用者"), 
                                        on_delete=models.CASCADE, 
                                        null=True, blank=True)
    guest_user = models.BooleanField(verbose_name='ゲスト', default=False)
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    