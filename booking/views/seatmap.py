import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse
from django.forms.models import model_to_dict

from ..models import Seat, Student, SystemUser

#ページ読み込み時の処理
#座席表のtdの背景のみ設定する
def get_seatmap_attribute(type):
    seatmap_attribute = [0]
    for i in range(1,55):
        if type == 'guest':
            #ゲストの退室処理の座席表
            seat = Seat.objects.get(seat_id=i)
            attribute = 'id="seat' + str(i) + '" '

            if seat.guest_user:
                attribute += 'class="bg-danger pickseat"'
        
        else:
            seat = Seat.objects.get(seat_id=i)
            attribute = 'id="seat' + str(i) + '" '

            if seat.status == Seat.AVAILABLE:
                attribute += 'class="bg-success"'
            
            if seat.status == Seat.TAKEN:
                if type == SystemUser.ADMIN and seat.internet == False:
                    #管理画面の座席表
                    attribute += 'class="bg-warning taken"'
                else:
                    attribute += 'class="bg-danger taken"'
            
            if seat.status == Seat.UNAVAILABLE:
                attribute += 'class="bg-secondary unavailable"'

        
        seatmap_attribute.append(attribute)
    return seatmap_attribute

#座席表を辞書型に変換
@login_required
def get_seatmap_dict(request):
    queryset = Seat.objects.all()
    data = {}
    for i in range(1,55):
        seat = Seat.objects.get(seat_id=i)
        seatdict = model_to_dict(seat)
        
        full_name = ""
        student_id = ""
        full_hr_class = ""

        #ゲストユーザーでない場合
        if seat.current_user is not None:
            full_name = seat.current_user.full_name()
            student_id = seat.current_user.student_id
            full_hr_class = seat.current_user.full_hr_class_and_num()

        #座席データのテーブルに利用者の情報を追加
        seatdict['full_name'] = full_name
        seatdict['student_id'] = student_id 
        seatdict['full_hr_class'] = full_hr_class 
        
        data[i] = seatdict
    
    return data

#jQuery更新処理
@login_required
def get_seatmap_json(request):
    #座席表入手
    data = get_seatmap_dict(request)
    jsondata = json.dumps(data, ensure_ascii=False) 
    return HttpResponse(jsondata, content_type="application/json")