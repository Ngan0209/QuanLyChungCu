from chungcu import serializers
from rest_framework import viewsets, generics
from  chungcu.models import *

class BuildingViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset =  Building.objects.filter(active = True)
    serializer_class = serializers.BuildingSerializer

class ApartmentViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset =  Apartment.objects.filter(active = True)
    serializer_class = serializers.ApartmentSerializer

class ResidentViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset =  Resident.objects.all()
    serializer_class = serializers.ResidentSerializer

class LockerItemViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset =  LockerItem.objects.all()
    serializer_class = serializers.LockerItemSerializer

class ParkingCardViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = ParkingCard.objects.all()
    serializer_class = serializers.ParkingCardSerializer