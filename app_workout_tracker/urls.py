from django.contrib import admin
from django.urls import path
from . import views

app_name= 'awt'
urlpatterns =[
    #Public view
    #Public topic List
    path('', views.public_topics_list, name='public_topics_list'),
    path('public_list/<int:topic_id>/subtopic_list/<str:subtopic_name>', views.public_subtopic_list, name='public_subtopic_list'),

    #Public topic detail
    path('public_list/<int:subtopic_id>/<str:subtopic_name>', views.public_subtopic_detail, name='public_subtopic_detail'),


    #Secure topic list

    #Secure topic detail
]