import re

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField
from rest_framework.exceptions import ValidationError


def validate_hours(value):
    if not re.match(r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]-(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", value):
        raise ValidationError(f'{value} is not a correct time interval')


class OrderStatus(models.IntegerChoices):
    NEW = 0, "new"
    ASSIGNED = 1, "assigned"
    COMPLETED = 2, "completed"


class Pack(models.Model):
    assign_time = models.DateTimeField()
    n_orders = models.PositiveIntegerField()
    completed_orders = models.PositiveIntegerField(default=0)

    @property
    def pack_id(self):
        return self.id


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
    last_timestamp = models.DateTimeField(null=True, blank=True)
    pack = models.ForeignKey(Pack, null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)

    @property
    def max_weight(self):
        return self.WEIGHT_CONSTRAINTS[self.courier_type][0]

    @property
    def coefficient(self):
        return self.WEIGHT_CONSTRAINTS[self.courier_type][1]


class Order(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True, validators=[MinValueValidator(1)])
    weight = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(50)])
    region = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    delivery_hours = ArrayField(models.CharField(max_length=12, validators=[validate_hours]))
    status = models.IntegerField(default=OrderStatus.NEW, choices=OrderStatus.choices)
    courier = models.ForeignKey(Courier, null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)
    pack = models.ForeignKey(Pack, null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)
