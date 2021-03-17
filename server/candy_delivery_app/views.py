from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from candy_delivery_app.models import Courier
from candy_delivery_app.serializers import CourierSerializer


class CourierView(APIView):

    def get(self, request, format=None):
        couriers = Courier.objects.all()
        serializer = CourierSerializer(couriers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CourierSerializer(data=request.data['data'], many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"couriers": list(map(lambda x: {"id": x["courier_id"]}, serializer.data))},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
