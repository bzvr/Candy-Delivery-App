from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from candy_delivery_app import views

urlpatterns = [
    path('couriers', views.CourierView.as_view()),
    path('couriers/<int:pk>', views.CourierView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/assign', views.AssignOrderView.as_view()),
    path('orders/complete', views.CompleteOrderView.as_view()),
]

