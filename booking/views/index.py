import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.forms.models import model_to_dict

from ..models import SystemUser
from . import seatmap

#メインページ
@login_required
def index(request):
    type = request.user.type

    if 'register_student_id' in request.session:
            del request.session['register_student_id']
    
    if 'internet' in request.session:
        del request.session['internet']

    #座席表　それぞれの座席のHTMLの属性を入手
    seatmap_attribute = seatmap.get_seatmap_attribute(type)
    context = {'seatmap_attribute': seatmap_attribute}


    if type == SystemUser.REGISTER:
        context['type'] = 'register'
        context['action_type'] = 'register_display'

        if 'message' in request.session:
            message = ''
            if request.session['message'] == 'check_in_success':
                message = '入室が完了しました。Check-in Completed'
            elif request.session['message'] == 'check_out_success':
                message = '退室が完了しました。Check-out Completed'

            context['message'] = message
            del request.session['message']

    elif type == SystemUser.ADMIN:
        context['type'] = 'admin'
        context['action_type'] = 'admin_display'
    
    elif type == SystemUser.DISPLAY:
        context['type'] = 'display'
        context['action_type'] = 'static_display'

    return render(request, 'booking/index.html', context)    