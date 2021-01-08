from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

app_name='users'
urlpatterns=[
    #Using Django's default login Page.
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('register/', views.registerView, name='register')
]