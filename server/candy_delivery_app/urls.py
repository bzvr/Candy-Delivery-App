from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from candy_delivery_app import views

urlpatterns = [
    re_path('couriers/?$', views.CourierView.as_view()),
    path('couriers/<int:pk>', views.CourierView.as_view()),
    re_path('orders/?$', views.OrderView.as_view()),
    re_path('orders/assign/?$', views.AssignOrderView.as_view()),
    re_path('orders/complete/?$', views.CompleteOrderView.as_view()),
]

