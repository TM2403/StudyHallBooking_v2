from django.urls import path

from .views import index, seatmap, admin_controls, register, edit_student



urlpatterns = [
    path('', index.index, name='index'),
    path('check_in/<int:step>', register.check_in, name='check_in'),
    path('check_out', register.check_out, name='check_out'),
    path('check_in/internet/<int:choice>', register.internet, name='internet'),
    path('check_in/seat/<int:seat>', register.pick_seat, name='check_in_seat'),
    path('check_in/seat/', register.pick_seat_empty, name='check_in_seat_empty'),
    path('student/<slug:type>', edit_student.student_info, name='student_info'),
    path('getseatmap/', seatmap.get_seatmap_json, name='getseatmap'),
    path('seat/<int:seat_id>', admin_controls.details, name='view_seat_details'),
    path('seat/', admin_controls.details_empty, name='seat_details_empty'),
    path('seat<int:seat_id>/internet', admin_controls.change_internet_status, name='change_internet_status'),
    path('seat/<int:seat_id>/vacant', admin_controls.make_seat_vacant, name='vacant_seat'),
    path('seat/<int:seat_id>/unavailable', admin_controls.make_seat_unavailable, name='unavailable_seat'),

    path('unavailable_seats', admin_controls.edit_unavailable_seats, name='unavailable_seatmap'),

    path('check_out_guest/', register.check_out_guest, name='check_out_guest'),
    path('check_out/seat/<int:seat>', register.pick_guest_seat, name='check_out_seat'),
    path('check_out/seat/', register.pick_guest_seat_empty, name='check_out_seat_empty'),
]