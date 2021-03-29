import itertools
import json
from datetime import datetime

from dateutil import parser
from django.db.models import F, QuerySet, Min, Avg
from django.db.transaction import atomic
from rest_framework.views import exception_handler

from candy_delivery_app.models import Courier, Order, OrderStatus, Pack

CLASS_NAME = {"CourierView": ("courier_id", "couriers"), "OrderView": ("order_id", "orders"),
              "StuffOrderView": ("order_id", "orders")}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    try:
        sid, name = CLASS_NAME[context['view'].__class__.__name__]
    except KeyError:
        print(f"NOT CUSTOM EXCEPTION: {response}")
        return response

    if response is not None:

        if isinstance(response.data, dict):
            oid = int(context["request"].get_full_path().split('/')[-1])
            customized_response = {'validation_error': {'id': oid, 'errors': []}}
            for key, value in response.data.items():
                customized_response['validation_error']['errors'].append({"field": key, "message": value})

        else:
            customized_response = {'validation_error': {name: []}}
            for i, obj in enumerate(response.data):
                if obj:
                    oid = context['request'].data['data'][i][sid]
                    error = {'id': oid, 'errors': []}
                    for key, value in obj.items():
                        error['errors'].append({"field": key, "message": value})
                    customized_response["validation_error"][name].append(error)

        response.data = customized_response
    return response


def is_time_overlapping(delivery_hours, working_hours):
    def overlap(first_inter, second_inter):
        for f, s in ((first_inter, second_inter), (second_inter, first_inter)):
            for t in f:
                if s[0] <= t <= s[1]:
                    return True
        else:
            return False

    def parse_time_string(time_string):
        t1, t2 = map(lambda x: parser.parse(x).time(), time_string.split('-'))
        return t1, t2

    combos = [overlap(int1, int2)
              for (i1, int1), (i2, int2)
              in itertools.product(enumerate(map(parse_time_string, working_hours)),
                                   enumerate(map(parse_time_string, delivery_hours)))]

    return any(combos)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()[:-6] + 'Z'
        return json.JSONEncoder.default(self, o)


@atomic
def save_multiple_objects(obj_list):
    for o in obj_list:
        if isinstance(o, list) or isinstance(o, QuerySet):
            for nested in o:
                nested.save()
        else:
            o.save()


def get_orders_for_pack(courier: Courier):
    retrieved = Order.objects.filter(status=OrderStatus.NEW, region__in=courier.regions,
                                     weight__range=(0.01, courier.max_weight)).order_by("-weight")
    current_weight = 0
    result = []
    for order in retrieved:
        if is_time_overlapping(order.delivery_hours,
                               courier.working_hours) and current_weight + order.weight <= courier.max_weight:
            result.append(order)
            current_weight += order.weight
    return result


def update_pack_after_patch(courier: Courier, redis_conn):
    pack = courier.order_pack
    orders_in_pack = Order.objects.filter(order_pack=pack, status=OrderStatus.ASSIGNED).order_by("-weight")
    current_weight = 0
    new_order_ids = []
    update = False

    for order in orders_in_pack:
        if not is_time_overlapping(order.delivery_hours,
                                   courier.working_hours) or \
                current_weight + order.weight > courier.max_weight or \
                order.region not in courier.regions:
            update = True
            order.courier = None
            order.order_pack.n_orders = F("n_orders") - 1
            order.order_pack.save()
            order.order_pack = None
            order.status = OrderStatus.NEW
        else:
            current_weight += order.weight
            new_order_ids.append(order.order_id)

    if update:
        data = json.loads(redis_conn.get(str(courier.courier_id)))
        data["orders"] = new_order_ids
        redis_conn.set(str(courier.courier_id), json.dumps(data, cls=DateTimeEncoder))

        if current_weight == 0:
            if pack.completed_orders > 0:
                courier.completed_order_packs = F("completed_order_packs") + 1
                courier.order_pack.is_completed = True
                courier.order_pack.save()

            courier.at_work = False
            courier.order_pack = None
            redis_conn.delete(str(courier.courier_id))

        save_multiple_objects([orders_in_pack, courier])


def calc_rating(courier: Courier):
    orders = Order.objects.filter(courier=courier).values('region').annotate(
        avg=Avg('complete_time_seconds')).order_by()
    t = min(orders, key=lambda x: x['avg'])['avg']
    return (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5


def calc_earnings(courier: Courier):
    earnings = 0
    order_packs = Pack.objects.filter(assigned_courier=courier, is_completed=True)
    for pack in order_packs:
        earnings += 500 * pack.coefficient
    return earnings
