from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone


from ..models import Seat, Student, Log
from ..forms import StudentIDForm
from . import seatmap

@login_required
def check_out(request):
    if request.user.type != 'register':
        return HttpResponseRedirect(reverse('index'))

    context = {
            'type': 'check_out',
            'step': 1,
    }

    if request.method == 'POST':
            form = StudentIDForm('check_out', request.POST)       
            if form.is_valid():
                student_id = form.clean().get('student_id')
                student = Student.objects.get(student_id=student_id)
                seat = Seat.objects.get(current_user=student)
                seat.status = 0
                seat.current_user = None
                seat.internet = False
                seat.guest_user = False
                seat.save()

                log = Log.objects.get(seat_id=seat.seat_id, guest_user=False, user=student, check_out_time__isnull=True)
                log.check_out_time = timezone.now()
                log.save()

                request.session['message'] = 'check_out_success'
                return HttpResponseRedirect(reverse('index'))

    else:
        form = StudentIDForm('check_out')

    context['form'] = form    
    return render(request, "booking/register.html", context)

@login_required
def check_out_guest(request):
    context = {
            'type': 'guest',
            'seatmap_attribute': seatmap.get_seatmap_attribute('guest'),
    }
    return render(request, "booking/register.html", context)

#For referencing pick_seat url without seat_id
def pick_guest_seat_empty(request):
    raise Http404()

@login_required
def pick_guest_seat(request, seat):
    if request.user.type != 'register':
        return HttpResponseRedirect(reverse('index'))
            
    seat = get_object_or_404(Seat, seat_id = seat)

    if seat.status == 1 and seat.guest_user == True:
        seat.status = 0
        seat.current_user = None
        seat.internet = False
        seat.guest_user = False
        seat.save()

        log = Log.objects.get(seat_id=seat.seat_id, guest_user=True, check_out_time__isnull=True)
        log.check_out_time = timezone.now()
        log.save()

        request.session['message'] = 'check_out_success'
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('check_out_guest'))


@login_required
def check_in(request, step): 
    if request.user.type != 'register':
        return HttpResponseRedirect(reverse('index'))

    context = {
            'type': 'check_in',
            'step': step,
    }

    if step == 1:
        if 'register_student_id' in request.session:
            del request.session['register_student_id']
        
        if 'internet' in request.session:
            del request.session['internet']

        if request.method == 'POST':
            form = StudentIDForm('check_in', request.POST)       
            if form.is_valid():
                student_id = form.clean().get('student_id')
                request.session['register_student_id'] = student_id
                if search_student(student_id):
                    return HttpResponseRedirect(reverse('check_in', args=(2,)))
                else:
                    return HttpResponseRedirect(reverse('student_info', args=('create',)))
        
        else:
            form = StudentIDForm('check_in')

        context['form'] = form
        
        return render(request, "booking/register.html", context)

    elif step == 2 or step == 3:
        if 'register_student_id' in request.session:
            student_id = request.session['register_student_id']
            student = Student.objects.get(student_id=student_id)
            context['student'] = student
        elif step == 2:
            return HttpResponseRedirect(reverse('check_in', args=(1,)))

        return render(request, "booking/register.html", context)

    elif step == 4:
        if 'register_student_id' in request.session and 'internet' in request.session:
            student_id = request.session['register_student_id']
            student = Student.objects.get(student_id=student_id)
            context['student'] = student

        
        context['internet'] = request.session['internet']
        context['seatmap_attribute'] = seatmap.get_seatmap_attribute('check_in')

        return render(request, "booking/register.html", context)

def search_student(student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        return True
    except Student.DoesNotExist:
        return False

def internet(request, choice):
    request.session['internet'] = choice
    return HttpResponseRedirect(reverse('check_in', args=(4,)))    

#For referencing pick_seat url without seat_id
def pick_seat_empty(request):
    raise Http404()

@login_required
def pick_seat(request, seat):
    if request.user.type != 'register':
        return HttpResponseRedirect(reverse('index'))

    if 'internet' in request.session:
        if 'register_student_id' in request.session:
            student_id = request.session['register_student_id'] 
            student = Student.objects.get(student_id=student_id)
            is_guest = False
            del request.session['register_student_id']
        else:
            student = None
            is_guest = True
            
        seat = Seat.objects.get(seat_id = seat)
        internet = request.session['internet']
        del request.session['internet']

        if seat.status == 0 and seat.current_user is None:
            seat.status = 1
            seat.current_user = student
            seat.internet = (internet == 1)
            seat.guest_user = is_guest
            seat.save()

            log = Log(seat_id=seat.seat_id, guest_user=is_guest, user=student, check_in_time=timezone.now())
            log.save()


            request.session['message'] = 'check_in_success'

            return HttpResponseRedirect(reverse('index'))

        else:
            return HttpResponseRedirect(reverse('check_in', args=(4,)))


    else:
        return HttpResponseRedirect(reverse('check_in', args=(1,)))

    