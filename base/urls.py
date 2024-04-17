from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.manager_home, name='manager_home' ),
    path('create_offer',views.create_offer, name='create_offer' ),
    path('create_category/<int:offer_id>/', views.create_category, name='create_category'),
    path('create_category',views.create_category, name='create_category' ),
    path('edit_category', views.edit_category, name='edit_category'),
    path('edit_category/<int:offer_id>/<int:category_id>/', views.edit_category, name='edit_category'),
    path('manager_home',views.manager_home, name='manager_home' ),
   
    path('my_schedule',views.my_schedule, name='my_schedule' ),
    path('offer_detail/<int:offer_id>',views.offer_detail, name='offer_detail' ),
    path('delete_category/<int:offer_id>/<int:category_id>', views.delete_category, name='delete_category'),
    path('delete_offer/<int:offer_id>', views.delete_offer, name='delete_offer'),
    path('new_reservation_timetable/<int:offer_id>/<int:category_id>', views.new_reservation_timetable, name='new_reservation_timetable'),
    path('new_reservation/<int:offer_id>/<int:category_id>', views.new_reservation, name='new_reservation'),
    path('new_reservation',views.new_reservation, name='new_reservation' ),
    path('managed_reservations',views.managed_reservations, name='managed_reservations' ),
    path('reservation-details/', views.reservation_details, name='reservation_details'),
    path('submit_reservation/', views.submit_reservation, name='submit_reservation'),
    path('verify_reservation/<str:token>/', views.verify_reservation, name='verify_reservation'),  # Assuming you have a verify_reservation view
    path('confirm_reservation/<str:token>/', views.confirm_reservation, name='confirm_reservation'),
    path('cancel_reservation/<str:token>/', views.cancel_reservation, name='cancel_reservation'),
    path('customer_home/<int:manager_id>', views.customer_home, name='customer_home'),
    path('manager_link/<int:manager_id>', views.manager_link, name='manager_link'),
    path('optimize', views.optimize, name='optimize'),
    path('reserve-slot', views.reserve_slot, name='reserve_slot'),
    path('save_optimization_strategy', views.save_optimization_strategy, name='save_optimization_strategy'),


   


    

    path('',include('users.urls'))
]