import json

from dateutil import parser
from redis import Redis
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from candy_delivery_app.models import Courier, Order, OrderStatus, Pack
from candy_delivery_app.serializers import CourierSerializer, OrderSerializer, StuffOrderSerializer
from candy_delivery_app.utils import is_time_overlapping, DateTimeEncoder

order_packs_db = Redis(host='redis', port=6379, db=0)


def get_orders_for_pack(courier: Courier):
    retrieved = Order.objects.filter(status=OrderStatus.NEW, region__in=courier.regions,
                                     weight__range=(0.01, courier.max_weight)).order_by("weight")
    current_weight = 0
    result = []
    for order in retrieved:
        if current_weight + order.weight > courier.max_weight:
            break
        if is_time_overlapping(order.delivery_hours, courier.working_hours):
            result.append(order)
            current_weight += order.weight
    return result


class CourierView(APIView):
    http_method_names = ["post", "get", "patch"]

    def get(self, request, pk=None):
        if pk is None:
            courier = Courier.objects.all()
            serializer = CourierSerializer(courier, many=True)
        else:
            try:
                courier = Courier.objects.get(courier_id=pk)
            except Courier.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = CourierSerializer(courier)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourierSerializer(data=request.data['data'], many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"couriers": list(map(lambda x: {"id": x["courier_id"]}, serializer.data))},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        courier = Courier.objects.get(courier_id=pk)
        serializer = CourierSerializer(courier, data=request.data,
                                       partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderView(APIView):
    http_method_names = ["post", "get"]

    def get(self, request, format=None):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data['data'], many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"orders": list(map(lambda x: {"id": x["order_id"]}, serializer.data))},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StuffOrderView(APIView):
    http_method_names = ["get"]

    def get(self, request, format=None):
        orders = Order.objects.all()
        serializer = StuffOrderSerializer(orders, many=True)
        return Response(serializer.data)


class AssignOrderView(APIView):
    http_method_names = ["post", "get"]

    def post(self, request, format=None):
        cid = request.data.get("courier_id", None)
        try:
            if cid is None:
                raise Courier.DoesNotExist
            courier = Courier.objects.get(courier_id=cid)

            if not order_packs_db.exists(str(courier.courier_id)):
                orders = get_orders_for_pack(courier)

                if not orders:
                    return Response({"orders": []}, status=status.HTTP_200_OK)

                order_ids = list(map(lambda x: x.order_id, orders))
                pack = {"orders": order_ids, "assign_time": now()}
                new_pack = Pack(assign_time=pack["assign_time"], n_orders=len(order_ids))
                new_pack.save()

                for order in orders:
                    order.status = OrderStatus.ASSIGNED
                    order.courier = courier
                    order.pack = new_pack
                    order.save()

                order_packs_db.set(str(courier.courier_id), json.dumps(pack, cls=DateTimeEncoder))

                courier.at_work = True
                courier.pack = pack
                courier.last_timestamp = pack["assign_time"]
                courier.save()

                return Response(
                    {"orders": list(map(lambda x: {"id": x}, order_ids)), "assign_time": pack["assign_time"]},
                    status=status.HTTP_200_OK)
            else:
                data = json.loads(order_packs_db.get(str(courier.courier_id)))
                return Response(
                    {"orders": list(map(lambda x: {"id": x}, data["orders"])), "assign_time": data["assign_time"]},
                    status=status.HTTP_200_OK)
        except Courier.DoesNotExist:
            return Response({"courier_id": f"courier with this courier id does not exist ({cid})"},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        counter = order_packs_db.incr('counter')
        return Response({"counter": counter})
