from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('addjob/', views.addjob, name='addjob'),
    path('jobs/', views.jobs, name='jobs'),
    path('viewjob/<int:id>/', views.viewjob, name='viewjob'),
    path('updatejob/<int:id>/', views.updatejob, name='updatejob'),
    path('deletejob/<int:id>/', views.deletejob, name='deletejob'),
    path('applyjob/<int:id>/', views.applyjob, name='applyjob'),
    path('viewapplications/', views.viewapplications, name='viewapplications'),
    path('viewjobapplications/', views.viewjobapplications, name='viewjobapplications'),
    path('send/<int:id>/', views.send, name='send'),
    path('reject/<int:id>/', views.reject, name='reject'),

    path('testandresponses/', views.testandresponses, name='testandresponses'),
    path('attempttest/<int:id>/', views.attempttest, name='attempttest'),
    path('viewtestresponse/<int:id>/', views.viewtestresponse, name='viewtestresponse'),
    path('selectcandidate/<int:id>/', views.selectcandidate, name='selectcandidate'),
    path('rejectcandidate/<int:id>/', views.rejectcandidate, name='rejectcandidate'),

    




    
]
