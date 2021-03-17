from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from candy_delivery_app import views

urlpatterns = [
    re_path('couriers/?$', views.CourierView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
