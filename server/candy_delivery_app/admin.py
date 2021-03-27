from django.contrib import admin

# Register your models here.
from candy_delivery_app.models import Courier, Order

admin.site.register(Courier)
admin.site.register(Order)