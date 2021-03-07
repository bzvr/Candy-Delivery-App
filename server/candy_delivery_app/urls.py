from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from candy_delivery_app import views

urlpatterns = [
    path('couriers/', views.CourierList.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
