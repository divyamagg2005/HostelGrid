from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('add/', views.room_add, name='room_add'),
    path('<int:pk>/', views.room_detail, name='room_detail'),
    path('<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('<int:pk>/delete/', views.room_delete, name='room_delete'),
]
