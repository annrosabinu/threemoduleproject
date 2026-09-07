
from django.urls import path
from .import views

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('loginpage',views.loginpage,name='loginpage'),
    path('loginauth',views.loginauth,name='loginauth'),
    path('tsignup',views.tsignup,name='tsignup'),
    path('stusignup',views.stusignup,name='stusignup'),
    path('addteacher',views.addteacher,name='addteacher'),
    path('addstudent',views.addstudent,name='addstudent'),
    path('adminhome',views.adminhome,name='adminhome'),
    path('tadmin',views.tadmin,name='tadmin'),
    path('sadmin',views.sadmin,name='sadmin'),
    path('approvedisapprove',views.approvedisapprove,name='approvedisapprove'),
    path('approve/<int:id>',views.approve,name='approve'),
    path('disapprove/<int:id>',views.disapprove,name='disapprove'),
    path('reset', views.reset, name='reset'),
    path('logout',views.logout,name='logout'),
]