from django.urls import path
from . import views

urlpatterns = [
    path('', views.complaint_list, name='complaint_list'),
    path('add/', views.complaint_add, name='complaint_add'),
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('<int:pk>/update/', views.complaint_update, name='complaint_update'),
    path('<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),
]
