from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home' ),
    path('create_offer',views.create_offer, name='create_offer' )
]