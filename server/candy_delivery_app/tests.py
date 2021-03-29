from django.test import TestCase
from rest_framework.test import APITestCase

from candy_delivery_app.models import Courier, Order


# Create your tests here...
def is_equal_courier(model, courier, assert_obj):
    assert_obj.assertEqual(model.courier_id, courier['courier_id'])
    assert_obj.assertEqual(model.courier_type, courier['courier_type'])
    assert_obj.assertEqual(model.regions, courier['regions'])
    assert_obj.assertEqual(model.working_hours, courier['working_hours'])
    assert_obj.assertEqual(model.completed_order_packs, 0)
    assert_obj.assertEqual(model.at_work, False)
    assert_obj.assertEqual(model.last_timestamp, None)
    assert_obj.assertEqual(model.order_pack, None)


def is_equal_order(model, order, assert_obj):
    assert_obj.assertEqual(model.order_id, order['order_id'])
    assert_obj.assertEqual(model.weight, order['weight'])
    assert_obj.assertEqual(model.region, order['region'])
    assert_obj.assertEqual(model.delivery_hours, order['delivery_hours'])
    assert_obj.assertEqual(model.status, 0)
    assert_obj.assertEqual(model.courier, None)
    assert_obj.assertEqual(model.order_pack, None)
    assert_obj.assertEqual(model.complete_time_seconds, None)


class CourierCreateTestCase(APITestCase):
    url = '/couriers'

    def setUp(self):
        courier = Courier(courier_id=1337, courier_type="car", regions=[1337],
                          working_hours=[])
        courier.save()

    def test_create_one_courier_normal(self):
        courier = {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }

        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        created_courier = Courier.objects.first()
        self.assertEqual(response.data['couriers'][0]['id'], created_courier.courier_id)
        is_equal_courier(created_courier, courier, self)

    def test_create_couriers_normal(self):
        data = {"data": [
            {
                "courier_id": 1,
                "courier_type": "car",
                "regions": [
                    1
                ],
                "working_hours": [
                    "08:00-22:00"
                ]
            },
            {
                "courier_id": 2,
                "courier_type": "foot",
                "regions": [
                    2
                ],
                "working_hours": [
                    "15:00-19:00"
                ]
            },
            {
                "courier_id": 3,
                "courier_type": "bike",
                "regions": [
                    1, 2, 1337
                ],
                "working_hours": [
                    "08:00-11:00",
                    "14:00-19:00"
                ]
            }
        ]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        for i, courier in enumerate(response.data['couriers']):
            courier_obj = Courier.objects.get(courier_id=courier["id"])
            is_equal_courier(courier_obj, data["data"][i], self)

    def test_unknown_field(self):
        courier = {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"],
            "meme": "lol"
        }
        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_missing_field(self):
        courier = {
            "courier_id": 1,
            "courier_type": "foot",
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }
        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_positive_integer_cid_field(self):
        courier = {
            "courier_id": -5,
            "regions": [1, 12, 22],
            "courier_type": "foot",
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }
        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_valid_courier_type_field(self):
        courier = {
            "courier_id": 1,
            "regions": [1, 12, 22],
            "courier_type": "lol",
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }
        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_valid_region_field(self):
        courier = {
            "courier_id": 1,
            "regions": [1, 12, "oaoaoa"],
            "courier_type": "bike",
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }
        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_valid_working_hours_field(self):
        courier = {
            "courier_id": 1,
            "regions": [1, 2, 3],
            "courier_type": "bike",
            "working_hours": ["11:35-14:05aaa", "9:00-11:00"]
        }
        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_unique_id_field(self):
        courier = {
            "courier_id": 1337,
            "regions": [1, 12, 22],
            "courier_type": "foot",
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        }
        data = {'data': [courier]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)


class OrderCreateTestCase(APITestCase):
    url = '/orders'

    def setUp(self):
        order = Order(order_id=1337, weight=1, region=1337,
                      delivery_hours=["09:00-18:00"])
        order.save()

    def test_create_one_order_normal(self):
        order = {
            "order_id": 1,
            "weight": 20,
            "region": 1,
            "delivery_hours": [
                "09:00-18:00"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        created_order = Order.objects.first()
        self.assertEqual(response.data['orders'][0]['id'], created_order.order_id)
        is_equal_order(created_order, order, self)

    def test_create_orders_normal(self):
        data = {"data": [
            {
                "order_id": 1,
                "weight": 20,
                "region": 1,
                "delivery_hours": [
                    "09:00-18:00"
                ]
            },
            {
                "order_id": 2,
                "weight": 25,
                "region": 1,
                "delivery_hours": [
                    "09:00-18:00"
                ]
            },
            {
                "order_id": 3,
                "weight": 4,
                "region": 2,
                "delivery_hours": [
                    "09:00-12:00",
                    "16:00-21:30"
                ]
            }
        ]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        for i, order in enumerate(response.data['orders']):
            order_obj = Order.objects.get(order_id=order["id"])
            is_equal_order(order_obj, data["data"][i], self)

    def test_unknown_field(self):
        order = {
            "order_id": 1,
            "weight": 20,
            "region": 1,
            "delivery_hours": [
                "09:00-18:00"
            ],
            "meme": 1337
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_missing_field(self):
        order = {
            "order_id": 2,
            "weight": 25,
            "delivery_hours": [
                "09:00-18:00"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_positive_integer_oid_field(self):
        order = {
            "order_id": "id",
            "weight": 25,
            "region": 1,
            "delivery_hours": [
                "09:00-18:00"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_weight_gt_50_field(self):
        order = {
            "order_id": 1,
            "weight": 1500,
            "region": 1,
            "delivery_hours": [
                "09:00-18:00"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_weight_lt_001_field(self):
        order = {
            "order_id": 1,
            "weight": 0.005,
            "region": 1,
            "delivery_hours": [
                "09:00-18:00"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_valid_region_field(self):
        order = {
            "order_id": 1,
            "weight": 5,
            "region": "meme",
            "delivery_hours": [
                "09:00-18:00"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_valid_delivery_hours_field(self):
        order = {
            "order_id": 3,
            "weight": 4,
            "region": 2,
            "delivery_hours": [
                "12:00",
                "016:00-21:30"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_unique_id_field(self):
        order = {
            "order_id": 1337,
            "weight": 4,
            "region": 2,
            "delivery_hours": [
                "12:00",
                "016:00-21:30"
            ]
        }
        data = {'data': [order]}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
