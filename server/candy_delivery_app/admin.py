from django.contrib import admin

# Register your models here.
from candy_delivery_app.models import Courier, NewOrder, AssignedOrder, CompletedOrder

admin.site.register(Courier)
admin.site.register(NewOrder)
admin.site.register(AssignedOrder)
admin.site.register(CompletedOrder)