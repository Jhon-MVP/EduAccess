from django.urls import path
from .views import select_accessibility

urlpatterns = [
    path("select/", select_accessibility, name="select_accessibility"),
]
