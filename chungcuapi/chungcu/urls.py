from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('building', views.BuildingViewSet, basename='building')
router.register('apartment', views.ApartmentViewSet, basename='apartment')
router.register('resident', views.ResidentViewSet, basename='resident')
router.register('lockeritem', views.LockerItemViewSet, basename='lockeritem')
router.register('parkingcard', views.ParkingCardViewSet, basename='parkingcard')



urlpatterns = [
    path('', include(router.urls)),
]