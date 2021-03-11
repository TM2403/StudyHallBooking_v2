from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone


from ..models import Seat, Student, Log, SystemUser
from ..forms import StudentIDForm
from . import seatmap

#退室用ページ
@login_required
def check_out(request):
    if request.user.type != SystemUser.REGISTER:
        return HttpResponseRedirect(reverse('index'))

    context = {
            'action_type': 'check_out',
            'step': 1,
    }

    #既にフォームを送信した場合
    if request.method == 'POST':
        form = StudentIDForm('check_out', request.POST)       
        if form.is_valid():
            #座席の空席処理
            student_id = form.clean().get('student_id')
            student = Student.objects.get(student_id=student_id)
            seat = Seat.objects.get(current_user=student)
            seat.status = Seat.AVAILABLE
            seat.current_user = None
            seat.internet = False
            seat.guest_user = False
            seat.save()

            #退室記録
            log = Log.objects.get(seat_id=seat.seat_id, guest_user=False, user=student, check_out_time__isnull=True)
            log.check_out_time = timezone.now()
            log.save()

            request.session['message'] = 'check_out_success'
            return HttpResponseRedirect(reverse('index'))

    #まだフォームを送信していない場合
    else:
        form = StudentIDForm('check_out')

    context['form'] = form    
    return render(request, "booking/register.html", context)

#ゲストアカウントが退室する場合のページ
@login_required
def check_out_guest(request):
    context = {
            'action_type': 'guest_check_out',
            'seatmap_attribute': seatmap.get_seatmap_attribute('guest'),
    }
    return render(request, "booking/register.html", context)

#Django HTML jQuery上でURLを呼び出すための pick_guest_seat() の引数がない空関数
def pick_guest_seat_empty(request):
    raise Http404()

#ゲストアカウントが退室時、座席を選択した後の処理
@login_required
def pick_guest_seat(request, seat):
    if request.user.type != SystemUser.REGISTER:
        return HttpResponseRedirect(reverse('index'))
            
    seat = get_object_or_404(Seat, seat_id = seat)

    if seat.status == Seat.TAKEN and seat.guest_user == True:
        #座席の空席処理
        seat.status = Seat.AVAILABLE
        seat.current_user = None
        seat.internet = False
        seat.guest_user = False
        seat.save()

        #退室記録
        log = Log.objects.get(seat_id=seat.seat_id, guest_user=True, check_out_time__isnull=True)
        log.check_out_time = timezone.now()
        log.save()

        request.session['message'] = 'check_out_success'
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('check_out_guest'))

#入室時のページ
@login_required
def check_in(request, step): 
    if request.user.type != SystemUser.REGISTER:
        return HttpResponseRedirect(reverse('index'))

    context = {
            'action_type': 'check_in',
            'step': step,
    }

    # 1. 学籍番号入力ページ
    if step == 1: 
        if 'register_student_id' in request.session:
            del request.session['register_student_id']
        
        if 'internet' in request.session:
            del request.session['internet']

        #既にフォームを送信した場合
        if request.method == 'POST':
            form = StudentIDForm('check_in', request.POST)       
            if form.is_valid():
                student_id = form.clean().get('student_id')
                request.session['register_student_id'] = student_id

                #アカウントが存在したらアカウント詳細ページへ、存在しなかったら新規登録画面へ
                if search_student(student_id):
                    return HttpResponseRedirect(reverse('check_in', args=(2,)))
                else:
                    return HttpResponseRedirect(reverse('student_info', args=('create',)))
        
        #まだフォームをしていない場合
        else:
            form = StudentIDForm('check_in')

        context['form'] = form
        
        return render(request, "booking/register.html", context)


    # 2. 生徒アカウント詳細ページ
    # 3. インターネット利用有無確認ページ
    elif step == 2 or step == 3:
        if 'register_student_id' in request.session:
            student_id = request.session['register_student_id']
            student = Student.objects.get(student_id=student_id)
            context['student'] = student
        elif step == 2:
            return HttpResponseRedirect(reverse('check_in', args=(1,)))

        return render(request, "booking/register.html", context)

    #4. 座席の選択ページ
    elif step == 4:
        if 'register_student_id' in request.session and 'internet' in request.session:
            student_id = request.session['register_student_id']
            student = Student.objects.get(student_id=student_id)
            context['student'] = student

        
        context['internet'] = request.session['internet']
        context['seatmap_attribute'] = seatmap.get_seatmap_attribute('check_in')

        return render(request, "booking/register.html", context)

#生徒アカウントが存在するか検索
def search_student(student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        return True
    except Student.DoesNotExist:
        return False

#インターネットの利用有無を選択した後の処理
def internet(request, choice):
    request.session['internet'] = choice
    return HttpResponseRedirect(reverse('check_in', args=(4,)))    

#Django HTML jQuery上でURLを呼び出すための pick_seat() の引数がない空関数
def pick_seat_empty(request):
    raise Http404()

#入室時、座席を選択した後の処理
@login_required
def pick_seat(request, seat):
    if request.user.type != SystemUser.REGISTER:
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

        if seat.status == Seat.AVAILABLE and seat.current_user is None:
            #座席の入室処理
            seat.status = Seat.TAKEN
            seat.current_user = student
            seat.internet = (internet == 1)
            seat.guest_user = is_guest
            seat.save()

            #入室記録
            log = Log(seat_id=seat.seat_id, guest_user=is_guest, user=student, check_in_time=timezone.now())
            log.save()


            request.session['message'] = 'check_in_success'

            return HttpResponseRedirect(reverse('index'))

        else:
            #座席が空席でない場合
            return HttpResponseRedirect(reverse('check_in', args=(4,)))


    else:
        #必要なデータがセッションにない場合
        return HttpResponseRedirect(reverse('check_in', args=(1,)))

    