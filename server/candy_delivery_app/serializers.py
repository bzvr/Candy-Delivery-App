from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.settings import api_settings

from candy_delivery_app.models import Courier, Order


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = [f"Unknown field: {f}" for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })

        return super(CourierSerializer, self).run_validation(data)

    def update(self, instance, validated_data):
        if 'courier_id' in validated_data:
            raise serializers.ValidationError({
                'courier_id': 'You must not change this field.',
            })
        return super(CourierSerializer, self).update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'weight', 'region', 'delivery_hours']

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = [f"Unknown field: {f}" for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })

        return super(OrderSerializer, self).run_validation(data)


class StuffOrderSerializer(serializers.ModelSerializer):
    courier = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)
    order_pack = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'weight', 'region', 'delivery_hours', 'status', 'courier', 'order_pack',
                  'complete_time_seconds']

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = [f"Unknown field: {f}" for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })

        return super(StuffOrderSerializer, self).run_validation(data)
