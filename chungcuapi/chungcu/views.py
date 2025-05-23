from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from chungcu import serializers, paginators, perms
from rest_framework import viewsets, generics, status, parsers, permissions
from  chungcu.models import *

class BuildingViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.CreateAPIView,
                      generics.DestroyAPIView, generics.UpdateAPIView):
    queryset =  Building.objects.filter(active = True)
    serializer_class = serializers.BuildingSerializer
    pagination_class = paginators.ItemPaginator
    permission_classes = [perms.IsAdminUser,permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.queryset

        q = self.request.query_params.get('q')
        if q:
            query = query.filter(name__icontains=q)
        building_id = self.request.query_params.get('building_id')
        if building_id:
            query = query.filter(building_id=building_id)

        return query

    @action(detail=True, methods=['get'], url_path='apartments')
    def get_apartments(self, request, pk):
        apartments = self.get_object().apartments.all()
        return Response(serializers.ApartmentSerializer(apartments, many=True).data, status=status.HTTP_200_OK)

class ApartmentViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.UpdateAPIView,
                       generics.DestroyAPIView, generics.ListAPIView, generics.CreateAPIView):
    queryset =  Apartment.objects.filter(active = True)
    serializer_class = serializers.ApartmentSerializer
    pagination_class = paginators.ItemPaginator

    def get_permissions(self):
        # Nếu admin đang thao tác, cho phép tất cả
        if self.request.user.is_staff:
            return [permissions.IsAuthenticated()]

        # Nếu là cư dân, kiểm tra quyền sở hữu
        if self.action in ['get_residents','retrieve']:
            return [permissions.IsAuthenticated(), perms.IsResidentOfApartment()]

        return [perms.IsAdminUser()]

    def get_queryset(self):
        query = self.queryset

        q = self.request.query_params.get('q')
        if q:
            query = query.filter(number__icontains=q)
        apart_id = self.request.query_params.get('apart_id')
        if apart_id:
            query = query.filter(apartment_id=apart_id)

        return query

    @action(detail=True, methods=['get'], url_path='residents',)
    def get_residents(self, request, pk):
        residents = self.get_object().residents.all()
        return Response(serializers.ResidentSerializer(residents, many=True).data, status=status.HTTP_200_OK)

class ResidentViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.CreateAPIView, generics.UpdateAPIView,
                      generics.DestroyAPIView, generics.ListAPIView):
    queryset =  Resident.objects.select_related('apartment').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.ResidentDetailSerializer
        return serializers.ResidentSerializer

    def get_permissions(self):
        # Nếu admin đang thao tác, cho phép tất cả
        if self.request.user.is_staff:
            return [permissions.IsAuthenticated()]

        # Nếu là cư dân, kiểm tra quyền sở hữu
        if self.action in ['retrieve', 'get_invoices', 'get_invoice_detail',
                           'get_parkingcard', 'get_lockeritem', 'get_item_detail',
                           'get_complaints','get_complaint_detail', 'get_answers','get_answer_detail']:
            return [permissions.IsAuthenticated(), perms.IsOwner()]

        return [perms.IsAdminUser()]

    @action(detail=True, methods=['get'], url_path='invoices')
    def get_invoices(self, request, pk):
        invoices = self.get_object().invoices.all()
        return Response(serializers.InvoiceSerializer(invoices, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='invoice/(?P<invoice_id>[^/.]+)')
    def get_invoice_detail(self, request, pk, invoice_id):
        resident = self.get_object()
        invoice = get_object_or_404(resident.invoices, pk=invoice_id)
        serializer = serializers.InvoiceDetailSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='parkingcard')
    def get_parkingcard(self, request, pk):
        parkingcard = self.get_object().parkingcard
        return Response(serializers.ParkingCardDetailSerializer(parkingcard).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='lockeritem')
    def get_lockeritem(self, request, pk):
        lockeritem = self.get_object().lockeritem
        return Response(serializers.LockerItemSerializer(lockeritem).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='lockeritem/item/(?P<item_id>[^/.]+)')
    def get_item_detail(self, request, pk, item_id):
        resident = self.get_object()
        item = get_object_or_404(resident.lockeritem.items, pk=item_id)
        serializer = serializers.ItemDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='complaints')
    def get_complaints(self, request, pk):
        complaints = self.get_object().complaint_set.all()
        return Response(serializers.ComplaintSerializer(complaints, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='complaints/(?P<complaint_id>[^/.]+)')
    def get_complaint_detail(self, request, pk, complaint_id):
        resident = self.get_object()
        complaint = get_object_or_404(resident.complaint_set, pk=complaint_id)
        serializer = serializers.ComplaintDetailSerializer(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='answers')
    def get_answers(self, request, pk=None):
        # Lấy resident cụ thể
        resident = self.get_object()
        user = resident.user

        # Lấy tất cả answers thông qua các survey responses của user đó
        answers = Answer.objects.filter(response__user=user)

        # Serialize và trả kết quả
        serializer = serializers.AnswerSerializer(answers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class LockerItemViewSet(viewsets.ModelViewSet):
    queryset =  LockerItem.objects.prefetch_related('items').all()
    serializer_class = serializers.LockerItemSerializer
    permission_classes = [perms.IsAdminUser]

class ParkingCardViewSet(viewsets.ModelViewSet):
    queryset = ParkingCard.objects.all()
    serializer_class = serializers.ParkingCardDetailSerializer
    permission_classes = [perms.IsAdminUser]

class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.prefetch_related('resident').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.VisitorDetailSerializer
        return serializers.VisitorSerializer

    permission_classes = [perms.IsAdminUser]

    @action(detail=True, methods=['get'], url_path='parkingcard')
    def get_parkingcard(self, request, pk):
        parkingcard = self.get_object().parkingcard
        return Response(serializers.ParkingCardDetailSerializer(parkingcard).data, status=status.HTTP_200_OK)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.prefetch_related('fee_type').all()
    serializer_class = serializers.InvoiceSerializer
    permission_classes = [perms.IsAdminUser]

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.ComplaintDetailSerializer
        return serializers.ComplaintSerializer

    def get_permissions(self):
        # Nếu admin đang thao tác, cho phép tất cả
        if self.request.user.is_staff:
            return [permissions.IsAuthenticated()]

        # Nếu là cư dân, kiểm tra quyền sở hữu
        if self.action in ['retrieve','list','update','partial_update', 'create']:
            return [permissions.IsAuthenticated(), perms.IsOwner()]

        return [perms.IsAdminUser()]

class ComplaintResponseViewSet(viewsets.ModelViewSet):
    queryset = ComplaintResponse.objects.all()
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.ComplaintResponseDetailSerializer
        return serializers.ComplaintResponseSerializer

    permission_classes = [perms.IsAdminUser]

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.SurveyDetailSerializer
        return serializers.SurveySerializer

    permission_classes = [perms.IsAdminUser]

class AnswerViewSet(viewsets.ViewSet,  RetrieveAPIView, ListAPIView):
    queryset = Answer.objects.all()
    serializer_class = serializers.AnswerSerializer

    permission_classes = [perms.IsAdminUser]

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, RetrieveAPIView, ListAPIView, ):
    queryset = User.objects.filter(is_active = True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        # Nếu admin đang thao tác, cho phép tất cả
        if self.request.user.is_staff:
            return [permissions.IsAuthenticated()]

        # Nếu là cư dân, kiểm tra quyền sở hữu
        if self.action in ['retrieve', 'get_current_user' ]:
            return [permissions.IsAuthenticated(), perms.IsOwner]

        return [perms.IsAdminUser()]

    @action(detail=False, methods=['get', 'patch'], url_path='current_user')
    def get_current_user(self, request):
        u = request.user
        if request.method.__eq__('PATCH'):
            for k,v in request.data.items():
                if k in ['first_name', 'last_name','username','avatar']:
                    setattr(u, k, v)
                elif k.__eq__('password'):
                     u.set_password(v)

            u.save()

        return Response(serializers.UserSerializer(request.user).data)
