from django.urls import path
from . import views

urlpatterns = [
    #path('bot/', views.tasks_chatbot, name='chat'),
    path('form',views.form),
    path('viewleaverequest',views.view_leave_request,name='viewleaverequest'),
    path('',views.chatbot,name='chatbot'),
    path('view_tasks',views.view_tasks,name='view_tasks'),
    
]

