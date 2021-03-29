import json

from dateutil import parser
from redis import Redis
from django.utils.timezone import now
from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from candy_delivery_app.models import Courier, Order, OrderStatus, Pack
from candy_delivery_app.serializers import CourierSerializer, OrderSerializer, StuffOrderSerializer
from candy_delivery_app.utils import is_time_overlapping, DateTimeEncoder, save_multiple_objects, get_orders_for_pack, \
    update_pack_after_patch, calc_rating, calc_earnings

order_packs_db = Redis(host='redis', port=6379, db=0)


class CourierView(APIView):
    http_method_names = ["post", "get", "patch"]

    def get(self, request, pk=None):
        try:
            courier = Courier.objects.get(courier_id=pk)
        except Courier.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CourierSerializer(courier)

        rating = {"rating": calc_rating(courier)} if courier.completed_order_packs else {}
        return Response({**serializer.data, **rating, "earnings": calc_earnings(courier)})

    def post(self, request):
        serializer = CourierSerializer(data=request.data['data'], many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"couriers": list(map(lambda x: {"id": x["courier_id"]}, serializer.data))},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            courier = Courier.objects.get(courier_id=pk)
        except Courier.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CourierSerializer(courier, data=request.data,
                                       partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if courier.order_pack:
                update_pack_after_patch(courier, order_packs_db)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderView(APIView):
    http_method_names = ["post"]

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
    http_method_names = ["post"]

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
                new_pack = Pack(assign_time=pack["assign_time"], n_orders=len(order_ids), assigned_courier=courier,
                                coefficient=courier.coefficient)

                for i in range(len(orders)):
                    orders[i].status = OrderStatus.ASSIGNED
                    orders[i].courier = courier
                    orders[i].order_pack = new_pack

                order_packs_db.set(str(courier.courier_id), json.dumps(pack, cls=DateTimeEncoder))

                courier.at_work = True
                courier.order_pack = new_pack
                courier.last_timestamp = pack["assign_time"]

                save_multiple_objects([new_pack, orders, courier])

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


class CompleteOrderView(APIView):
    http_method_names = ["post"]

    def post(self, request, format=None):
        cid = request.data.get("courier_id", None)
        oid = request.data.get("order_id", None)
        try:
            complete_time = parser.isoparse(request.data.get("assign_time", None))
            if cid is None:
                raise Courier.DoesNotExist
            if oid is None:
                raise Order.DoesNotExist

            courier = Courier.objects.get(courier_id=cid)
            order = Order.objects.get(order_id=oid)

            if order.status != OrderStatus.ASSIGNED or order.courier != courier or not courier.at_work:
                raise Exception

            data = json.loads(order_packs_db.get(str(courier.courier_id)))
            complete_seconds = (complete_time - courier.last_timestamp).total_seconds()
            data['orders'] = list(filter(lambda x: x != order.order_id, data['orders']))
            order_packs_db.set(str(courier.courier_id), json.dumps(data, cls=DateTimeEncoder))

            order.order_pack.completed_orders = F("completed_orders") + 1
            order.complete_time_seconds = complete_seconds
            order.status = OrderStatus.COMPLETED
            courier.last_timestamp = complete_time

            if not data['orders']:
                courier.completed_order_packs = F("completed_order_packs") + 1
                order.order_pack.is_completed = True
                courier.at_work = False
                courier.order_pack = None
                order_packs_db.delete(str(courier.courier_id))

            save_multiple_objects([order.order_pack, order, courier])

            return Response({"order_id": order.order_id}, status=status.HTTP_200_OK)

        except (Courier.DoesNotExist, Order.DoesNotExist, Exception) as e:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
