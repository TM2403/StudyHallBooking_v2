from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, Http404
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone


from ..models import Seat, Student, Log
from . import seatmap

@login_required
def details(request, seat_id):
    if request.user.type != 'admin':
        return HttpResponseRedirect(reverse('index'))

    request.session['edit_from'] = 'details'

    seat = get_object_or_404(Seat, seat_id=seat_id)
    status_display = get_status_display(seat.status)
    logs = Log.objects.filter(seat_id=seat_id).order_by('-check_in_time')[:20]

    context = {
        'seat': seat,
        'current_status': status_display,
        'logs': logs, 
    }

    return render(request, 'booking/seat_details.html', context)


@login_required
def edit_unavailable_seats(request):
    if request.user.type != 'admin':
        return HttpResponseRedirect(reverse('index'))

    request.session['edit_from'] = 'seatmap'
    
    seatmap_attribute = seatmap.get_seatmap_attribute('unavailable_seats')
    context = {
        'seatmap_attribute': seatmap_attribute,
        'type': 'unavailable_seatmap',
    }

    return render(request, 'booking/unavailable_seats.html', context)
    

@login_required
def details_empty(request):
    raise Http404()

@login_required
def make_seat_vacant(request, seat_id):
    if request.user.type != 'admin':
        return HttpResponseRedirect(reverse('index'))

    seat = get_object_or_404(Seat, seat_id=seat_id)
    if seat.status == 1:
        log = Log.objects.get(seat_id=seat.seat_id, check_out_time__isnull=True)
        log.check_out_time = timezone.now()
        log.save()

    seat.current_user = None
    seat.internet = False
    seat.status = 0
    seat.save()
    if request.session['edit_from'] == 'details':
        return HttpResponseRedirect(reverse('view_seat_details', args=(seat_id,)))      
    else:
        return HttpResponseRedirect(reverse('unavailable_seatmap'))

@login_required
def make_seat_unavailable(request, seat_id):
    if request.user.type != 'admin':
        return HttpResponseRedirect(reverse('index'))
    
    seat = get_object_or_404(Seat, seat_id=seat_id)
    if seat.status != 1:
        seat.status = 9
    seat.save()

    if request.session['edit_from'] == 'details':
        return HttpResponseRedirect(reverse('view_seat_details', args=(seat_id,)))      
    else:
        return HttpResponseRedirect(reverse('unavailable_seatmap'))

@login_required
def change_internet_status(request, seat_id):
    if request.user.type != 'admin':
        return HttpResponseRedirect(reverse('index'))
    
    seat = get_object_or_404(Seat, seat_id=seat_id)
    seat.internet = (seat.internet == False)
    seat.save()
    return HttpResponseRedirect(reverse('view_seat_details', args=(seat_id,)))      

def get_status_display(status):
    status_display = ''

    if status == 0:
        status_display = "空席"
    elif status == 1:
        status_display = "使用中"
    elif status == 2:
        status_display = "予約"
    elif status == 9:
        status_display = "使用不可"
    
    return status_display
