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
    path('new_reservation',views.new_reservation, name='new_reservation' ),
    path('my_schedule',views.my_schedule, name='my_schedule' ),
    path('offer_detail/<int:offer_id>',views.offer_detail, name='offer_detail' ),
    path('delete_category/<int:offer_id>/<int:category_id>', views.delete_category, name='delete_category'),
    path('delete_offer/<int:offer_id>>', views.delete_offer, name='delete_offer'),


    

    path('',include('users.urls'))
]