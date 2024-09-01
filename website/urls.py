from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('originator/', views.originator_view, name='originator'),
    path('originator/form/', views.originate_view, name='originate_form'),  # Updated to use originate_view
    path('mark/', views.mark_view, name='mark'),
    path('pending/', views.pending_view, name='pending'),
    path('completed/', views.completed_view, name='completed'),
    path('adm_clearance/', views.adm_clearance_view, name='adm_clearance'),
    path('under_clearance/', views.under_clearance_view, name='under_clearance'),
]
