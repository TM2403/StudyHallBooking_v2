from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import SystemUser, Student, Seat, Log

#生徒アカウントの編集画面
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'last_name', 'first_name')
    fieldsets = (
        (None, {'fields': ('student_id',)}),
        ('Personal info', {'fields': ('last_name', 'first_name', 'hr_grade', 'hr_class', 'student_num')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'last_name', 'first_name', 'hr_grade', 'hr_class', 'student_num',),
        }),
    )
    search_fields = ('student_id', 'last_name', 'first_name',)

#管理ユーザーアカウントの編集画面
class SystemUserAdmin(UserAdmin):
    model = SystemUser
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('type',)}),)
    list_display = ['username', 'type']

#座席情報の編集画面（デバッグ専用）
class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_id', 'current_user', 'status', 'internet', )
    fieldsets = [
        ('座席番号', {'fields': ['seat_id']}),
        ('現在の利用者', {'fields': ['current_user']}),
        ('ゲスト', {'fields': ['guest_user']}),
        ('ステータス', {'fields': ['status']}),
        ('インターネット利用', {'fields': ['internet']}),
    ]
    ordering = (('seat_id', ))
    search_fields = ['current_user']

#入退記録の編集画面（デバッグ専用）
class LogAdmin(admin.ModelAdmin):
    list_display = ('seat_id', 'user', 'guest_user', 'check_in_time', 'check_out_time')
    fieldsets = [
        ('座席番号', {'fields': ['seat_id']}),
        ('利用者', {'fields': ['user']}),
        ('ゲスト', {'fields': ['guest_user']}),
        ('入室日時', {'fields': ['check_in_time']}),
        ('退室日時', {'fields': ['check_out_time']}),
    ]
    ordering = (('seat_id', ))
    search_fields = ['user']


#管理画面に追加
admin.site.register(Student, StudentAdmin)
admin.site.register(SystemUser, SystemUserAdmin)

#以下はデバッグ専用
#admin.site.register(Seat, SeatAdmin)
#admin.site.register(Log, LogAdmin)