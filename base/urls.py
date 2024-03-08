from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.manager_home, name='manager_home' ),
    path('create_offer',views.create_offer, name='create_offer' ),
    path('manager_home',views.manager_home, name='manager_home' ),
    path('new_reservation',views.new_reservation, name='new_reservation' ),
    path('my_schedule',views.my_schedule, name='my_schedule' ),
    
    path('',include('users.urls'))
]