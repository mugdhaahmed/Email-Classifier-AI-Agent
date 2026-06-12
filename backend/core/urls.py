from django.contrib import admin
from django.urls import path
from agent import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # REST API endpoint for initial frontend dashboard data hydration
    path('api/notifications/', views.important_notifications_list, name='notifications-list'),
]
