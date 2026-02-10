from django.urls import path
from .views import student_home, teacher_home

urlpatterns = [
    path("", student_home, name="student_home"),
    path("teacher/", teacher_home, name="teacher_home"),
]

