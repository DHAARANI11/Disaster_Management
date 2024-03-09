from django.urls import path
from .views import SignInView,SignUpView,Team

urlpatterns=[
    path('signin/',SignInView.as_view()),
    path('signup/',SignUpView.as_view()),
    path('team/', Team.as_view()),

]