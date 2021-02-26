from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


from ..models import Seat, Student
from ..forms import StudentEditForm
from . import seatmap

@login_required
def student_info(request, type):
    if 'register_student_id' in request.session:
        student_id = request.session['register_student_id']
    else:
        return HttpResponseRedirect(reverse('check_in', args=(1,)))

    if request.method == 'POST' or type == 'edit':
        if request.method == 'POST':
            form = StudentEditForm(request.POST)
            if form.is_valid():
                try:
                    student = Student.objects.get(student_id=student_id)
                    if type == 'create':
                        return HttpResponseRedirect(reverse('check_in', args=(1,)))

                    student.last_name = form.clean().get('last_name')
                    student.first_name = form.clean().get('first_name')
                    student.hr_grade = form.clean().get('hr_grade')
                    student.hr_class = form.clean().get('hr_class')
                    student.student_num = form.clean().get('student_num')
                    student.save()
                    
                except Student.DoesNotExist:
                    last_name = form.clean().get('last_name')
                    first_name = form.clean().get('first_name')
                    hr_grade = form.clean().get('hr_grade')
                    hr_class = form.clean().get('hr_class')
                    student_num = form.clean().get('student_num')
                    student = Student(student_id=student_id, last_name=last_name, first_name=first_name, hr_grade=hr_grade, hr_class=hr_class, student_num=student_num)
                    student.save() 
                return HttpResponseRedirect(reverse('check_in', args=(3,)))
            else:
                print(form.errors)
        elif type == 'edit':
            student = Student.objects.get(student_id=student_id)
            initial_dict = {
                'last_name': student.last_name,
                'first_name': student.first_name,
                'hr_grade': student.hr_grade,
                'hr_class': student.hr_class,
                'student_num': student.student_num,
            }
            form = StudentEditForm(initial=initial_dict)

    else:
        form = StudentEditForm()

    context = {
        'form': form,
        'student_id': student_id
    }

    if type == 'create':
        context['type'] = 'create'
    elif type == 'edit':
        context['type'] = 'edit'

    return render(request, "booking/edit_student.html", context)