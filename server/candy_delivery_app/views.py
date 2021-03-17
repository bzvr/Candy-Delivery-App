from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from candy_delivery_app.models import Courier, NewOrder
from candy_delivery_app.serializers import CourierSerializer, NewOrderSerializer


class CourierView(APIView):

    def get(self, request, pk=None):
        if pk is None:
            courier = Courier.objects.all()
            serializer = CourierSerializer(courier, many=True)
        else:
            courier = Courier.objects.get(courier_id=pk)
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


class NewOrderView(APIView):

    def get(self, request, format=None):
        orders = NewOrder.objects.all()
        serializer = NewOrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = NewOrderSerializer(data=request.data['data'], many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"orders": list(map(lambda x: {"id": x["order_id"]}, serializer.data))},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
