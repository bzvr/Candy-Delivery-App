from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField
import re

from rest_framework.exceptions import ValidationError


def validate_hours(value):
    if not re.match(r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]-(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", value):
        raise ValidationError(f'{value} is not a correct time interval')


class Courier(models.Model):
    COURIER_TYPES = (
        ("foot", "foot"),
        ("bike", "bike"),
        ("car", "car")
    )
    WEIGHT_CONSTRAINTS = {"foot": (10, 2), "bike": (15, 5), "car": (50, 9)}

    courier_id = models.PositiveIntegerField(primary_key=True, validators=[MinValueValidator(1)])
    courier_type = models.CharField(max_length=5, choices=COURIER_TYPES)
    regions = ArrayField(models.PositiveIntegerField(validators=[MinValueValidator(1)]))
    working_hours = ArrayField(models.CharField(max_length=12, validators=[validate_hours]), default=list, blank=True)
    completed_order_packs = models.PositiveIntegerField(default=0)
    at_work = models.BooleanField(default=False)
    last_timestamp = models.TimeField(null=True, blank=True)

    @property
    def max_weight(self):
        return self.WEIGHT_CONSTRAINTS[self.courier_type][0]

    @property
    def coefficient(self):
        return self.WEIGHT_CONSTRAINTS[self.courier_type][1]


class NewOrder(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True, validators=[MinValueValidator(1)])
    weight = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(50)])
    region = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    delivery_hours = ArrayField(models.CharField(max_length=12, validators=[validate_hours]))


class AssignedOrder(NewOrder):
    courier = models.ForeignKey("Courier", on_delete=models.CASCADE)


class CompletedOrder(AssignedOrder):
    pass
