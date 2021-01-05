from django.contrib import admin
from django.urls import path
from . import views

app_name= 'awt'
urlpatterns =[
    ##**************PUBLIC VIEW***********##
    # Public topic List
    path('', views.public_topics_list, name='public_topics_list'),
    # Public sub_topic list
    path('public_list/<int:topic_id>/subtopic_list/<str:subtopic_name>', views.public_subtopic_list, name='public_subtopic_list'),
    # Public sub_topic detail
    path('public_list/<int:subtopic_id>/<str:subtopic_name>', views.public_subtopic_detail, name='public_subtopic_detail'),
    ## ************SECURE VIEW************ ##
    # Secure topic list
    path('secure_list/', views.secure_topics_list.as_view(), name='secure_topics_list'),
    # Secure sub_topic list
    path('secure_list/<int:topic_id>/subtopic_list/<str:subtopic_name>', views.secure_subtopic_list.as_view(), name='secure_subtopic_list'),
    # Secure sub_topic detail
    path('secure_list/<int:pk>/<str:subtopic_name>',views.secure_subtopic_detail, name='secure_subtopic_detail'),
            ##(The DetailView generic view expects the primary key value captured from the URL to be called "pk")##

    # Secure topic add
    path('add_topic/', views.add_topic, name='add_topic'),
    # Secure topic delete
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    # Secure subtopic add
    path('add_subtopic/<int:topic_id>/', views.add_subtopic, name='add_subtopic')
    # Secure subtopic edit
    # Secure subtopic delete

]