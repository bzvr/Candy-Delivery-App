from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Courier(models.Model):
    COURIER_TYPES = (
        ("foot", "foot"),
        ("bike", "bike"),
        ("car", "car")
    )
    WEIGHT_CONSTRAINTS = {"foot": (10, 2), "bike": (15, 5), "car": (50, 9)}

    courier_id = models.PositiveIntegerField(primary_key=True)
    courier_type = models.CharField(max_length=5, choices=COURIER_TYPES)
    regions = ArrayField(models.PositiveIntegerField())
    working_hours = ArrayField(models.CharField(max_length=12))
    completed_orders = models.PositiveIntegerField(default=0)

    @property
    def max_weight(self):
        return self.WEIGHT_CONSTRAINTS[self.courier_type][0]

    @property
    def coefficient(self):
        return self.WEIGHT_CONSTRAINTS[self.courier_type][1]


class NewOrder(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True)
    weight = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(50)])
    region = models.PositiveIntegerField()
    delivery_hours = ArrayField(models.CharField(max_length=12))


class AssignedOrder(NewOrder):
    courier = models.ForeignKey("Courier", on_delete=models.CASCADE)


class CompletedOrder(AssignedOrder):
    pass
