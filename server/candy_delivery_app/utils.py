import itertools
import json
from datetime import datetime

from dateutil import parser
from django.db.transaction import atomic
from rest_framework.views import exception_handler

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
            return o.isoformat()[:-10] + 'Z'
        return json.JSONEncoder.default(self, o)


@atomic
def save_multiple_objects(obj_list):
    for o in obj_list:
        if isinstance(o, list):
            for nested in o:
                nested.save()
        else:
            o.save()
