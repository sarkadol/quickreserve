from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.manager_home, name='manager_home' ),
    path('create_offer',views.create_offer, name='create_offer' ),
    path('create_unit/<int:offer_id>/', views.create_unit, name='create_unit'),
    path('create_unit',views.create_unit, name='create_unit' ),
    path('edit_unit', views.edit_unit, name='edit_unit'),
    path('edit_unit/<int:offer_id>/<int:unit_id>/', views.edit_unit, name='edit_unit'),
    path('manager_home',views.manager_home, name='manager_home' ),
    path('new_reservation',views.new_reservation, name='new_reservation' ),
    path('my_schedule',views.my_schedule, name='my_schedule' ),
    path('offer_detail/<int:offer_id>',views.offer_detail, name='offer_detail' ),

    

    path('',include('users.urls'))
]