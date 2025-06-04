from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('buildings', views.BuildingViewSet, basename='building')
router.register('apartments', views.ApartmentViewSet, basename='apartment')
router.register('residents', views.ResidentViewSet, basename='resident')
router.register('lockeritems', views.LockerItemViewSet, basename='lockeritem')
router.register('items', views.ItemViewSet, basename='item')
router.register('parkingcards', views.ParkingCardViewSet, basename='parkingcard')
router.register('visitors', views.VisitorViewSet, basename='visitor')
router.register('invoices', views.InvoiceViewSet, basename='invoice')
router.register('complaints', views.ComplaintViewSet, basename='complaint')
router.register('complaintresponses', views.ComplaintResponseViewSet, basename='complaintresponse')
router.register('surveys', views.SurveyViewSet, basename='survey')

router.register('users', views.UserViewSet, basename='user')



urlpatterns = [
    path('', include(router.urls)),
]