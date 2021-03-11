from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, Http404
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone


from ..models import Seat, Student, Log, SystemUser
from . import seatmap

#Django HTML jQuery上でURLを呼び出すための details() の引数がない空関数
@login_required
def details_empty(request):
    raise Http404()

#管理者用　座席の詳細ページ
@login_required
def details(request, seat_id):
    if request.user.type != SystemUser.ADMIN:
        return HttpResponseRedirect(reverse('index'))

    request.session['edit_from'] = 'details'

    seat = get_object_or_404(Seat, seat_id=seat_id)
    status_display = get_status_display(seat.status)

    #ログは20件まで表示（変更可能）
    logs = Log.objects.filter(seat_id=seat_id).order_by('-check_in_time')[:20]

    context = {
        'seat': seat,
        'current_status': status_display,
        'logs': logs, 
    }

    return render(request, 'booking/seat_details.html', context)


#利用不可にする座席を座席表から選択するページ
@login_required
def edit_unavailable_seats(request):
    if request.user.type != SystemUser.ADMIN:
        return HttpResponseRedirect(reverse('index'))

    request.session['edit_from'] = 'seatmap'
    
    seatmap_attribute = seatmap.get_seatmap_attribute('unavailable_seats')
    context = {
        'seatmap_attribute': seatmap_attribute,
        'action_type': 'unavailable_seatmap',
    }

    return render(request, 'booking/unavailable_seats.html', context)
    

#座席を強制的に空席にする処理
@login_required
def make_seat_vacant(request, seat_id):
    if request.user.type != SystemUser.ADMIN:
        return HttpResponseRedirect(reverse('index'))

    seat = get_object_or_404(Seat, seat_id=seat_id)
    if seat.status == Seat.TAKEN:
        #退室記録
        log = Log.objects.get(seat_id=seat.seat_id, check_out_time__isnull=True)
        log.check_out_time = timezone.now()
        log.save()

    #空席処理
    seat.current_user = None
    seat.internet = False
    seat.status = Seat.AVAILABLE
    seat.save()
    
    if request.session['edit_from'] == 'details':
        #座席の詳細画面から飛んできた場合
        return HttpResponseRedirect(reverse('view_seat_details', args=(seat_id,)))      
    else:
        #座席表から飛んできた場合
        return HttpResponseRedirect(reverse('unavailable_seatmap'))

#座席を利用不可にする処理
@login_required
def make_seat_unavailable(request, seat_id):
    if request.user.type != SystemUser.ADMIN:
        return HttpResponseRedirect(reverse('index'))
    
    seat = get_object_or_404(Seat, seat_id=seat_id)
    if seat.status != Seat.TAKEN:
        seat.status = Seat.UNAVAILABLE
    seat.save()

    
    if request.session['edit_from'] == 'details':
        #座席の詳細画面から飛んできた場合
        return HttpResponseRedirect(reverse('view_seat_details', args=(seat_id,)))      

    else:
        #座席表から飛んできた場合
        return HttpResponseRedirect(reverse('unavailable_seatmap'))

#インターネット利用有無の変更処理
@login_required
def change_internet_status(request, seat_id):
    if request.user.type != SystemUser.ADMIN:
        return HttpResponseRedirect(reverse('index'))
    
    seat = get_object_or_404(Seat, seat_id=seat_id)
    seat.internet = (seat.internet == False)
    seat.save()
    return HttpResponseRedirect(reverse('view_seat_details', args=(seat_id,)))      

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

#座席のステータスの日本語表記
def get_status_display(status):
    status_display = ''

    if status == Seat.AVAILABLE:
        status_display = "空席"
    elif status == Seat.TAKEN:
        status_display = "使用中"
    elif status == Seat.UNAVAILABLE:
        status_display = "使用不可"
    
    return status_display
