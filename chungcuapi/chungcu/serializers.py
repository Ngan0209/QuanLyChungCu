from rest_framework.serializers import ModelSerializer
from chungcu.models import *

class BuildingSerializer(ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name','create_time','update_time']

class ApartmentSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['id', 'number','household_head','create_time','update_time']

class ResidentSerializer(ModelSerializer):
    class Meta:
        model = Resident
        fields = ['id', 'name','apartment', 'relationship_to_head']

class LockerItemSerializer(ModelSerializer):
    class Meta:
        model = LockerItem
        fields = ['id', 'locker_number','resident', 'status']

class ParkingCardSerializer(ModelSerializer):
    class Meta:
        model = ParkingCard
        fields = ['id', 'card_number','resident', 'vehicle_type']

