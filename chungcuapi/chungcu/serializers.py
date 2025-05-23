from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from chungcu.models import *

class IamgeSerializer(ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.url if instance.image else ''
        return data


class BuildingSerializer(ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name','create_time','update_time']

class ApartmentSerializer(ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['id', 'number','household_head','create_time','update_time']

class ResidentSerializer(ModelSerializer):
    apartment = ApartmentSerializer(many=False)
    class Meta:
        model = Resident
        fields = ['id', 'name','apartment', 'relationship_to_head']

class ResidentDetailSerializer(ResidentSerializer):
    class Meta:
        model = ResidentSerializer.Meta.model
        fields = ResidentSerializer.Meta.fields + ['identity_card','gender','phone']

class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name_item']

class LockerItemSerializer(ModelSerializer):
    items = ItemSerializer(many=True)
    class Meta:
        model = LockerItem
        fields = ['id', 'locker_number','resident', 'items']

class ItemDetailSerializer(ModelSerializer):
    class Meta:
        model = ItemSerializer.Meta.model
        fields = ItemSerializer.Meta.fields + ['status','received_at']

class ParkingCardSerializer(ModelSerializer):
    class Meta:
        model = ParkingCard
        fields = ['id', 'card_number','resident','visitor']

class ParkingCardDetailSerializer(ParkingCardSerializer):
    class Meta:
        model = ParkingCardSerializer.Meta.model
        fields = ParkingCardSerializer.Meta.fields + ['vehicle_type','license_plate', 'color']

class VisitorSerializer(ModelSerializer):
    resident = ResidentSerializer(many=False)
    class Meta:
        model = Visitor
        fields = ['id','full_name','resident', 'relationship_to_resident']

class VisitorDetailSerializer(VisitorSerializer):
    parking_card = ParkingCardSerializer(many=False)
    class Meta:
        model = VisitorSerializer.Meta.model
        fields = VisitorSerializer.Meta.fields + ['identity_card','phone','parking_card']


class FeeTypeSerializer(ModelSerializer):
    class Meta:
        model = FeeType
        fields = ['id', 'name']

class InvoiceSerializer(ModelSerializer):
    fee_type = FeeTypeSerializer(many=False)
    class Meta:
        model = Invoice
        fields = ['id','resident','fee_type','amount']

class InvoiceDetailSerializer(InvoiceSerializer):
    class Meta:
        model = InvoiceSerializer.Meta.model
        fields = InvoiceSerializer.Meta.fields + ['paid','due_date']

class ComplaintResponseSerializer(ModelSerializer):
    class Meta:
        model = ComplaintResponse
        fields = ['id', 'responder','content','create_time']

class ComplaintSerializer(ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'resident', 'title', 'status', 'is_resolved', 'create_time']
        read_only_fields = ['resident', 'create_time']

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if not user.is_staff:
            # Cư dân không được cập nhật status hoặc is_resolved
            validated_data.pop('status', None)
            validated_data.pop('is_resolved', None)

        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        validated_data['is_resolved'] = False
        return super().create(validated_data)

class ComplaintDetailSerializer(ComplaintSerializer):
    responses = ComplaintResponseSerializer(many=True, read_only=True)
    class Meta:
        model = ComplaintSerializer.Meta.model
        fields = ComplaintSerializer.Meta.fields + ['content','responses']

class ComplaintResponseDetailSerializer(ComplaintResponseSerializer):
    complaint = ComplaintSerializer(many=False)
    class Meta:
        model = ComplaintResponseSerializer.Meta.model
        fields = ComplaintResponseSerializer.Meta.fields + ['complaint']

class ChoiceSerializer(ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id','text']

class QuestionSerializer(ModelSerializer):
    # choices = ChoiceSerializer(many=True)
    class Meta:
        model = Question
        fields = ['id','text']

class SurveySerializer(ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id','title']

class SurveyDetailSerializer(SurveySerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = SurveySerializer.Meta.model
        fields = SurveySerializer.Meta.fields + ['questions']

class SurveyResponseSerializer(ModelSerializer):
    survey = SurveySerializer(many=True)
    class Meta:
        model = SurveyResponse
        fields = ['id','survey']

class AnswerSerializer(ModelSerializer):
    choices = ChoiceSerializer(many=True)
    class Meta:
        model = Answer
        fields = ['id','response','question','choices']

class UserSerializer(ModelSerializer):
    resident = PrimaryKeyRelatedField(queryset=Resident.objects.all(),
                                                  write_only=True)  # Chỉ chọn resident có sẵn

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'avatar', 'resident']
        extra_kwargs = {'password': {'write_only': True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar'] = instance.avatar.url if instance.avatar else ''

        # Kiểm tra nếu instance có thuộc tính resident
        if hasattr(instance, 'resident'):
            data['resident'] = ResidentSerializer(instance.resident).data
        else:
            data['resident'] = None
        return data

    def create(self, validated_data):
        resident = validated_data.pop('resident', None)  # Lấy resident từ validated_data
        password = validated_data.pop('password', None)
        avatar = validated_data.pop('avatar', None)

        user = User(**validated_data)
        if password:
            user.set_password(password)
        if avatar:
            user.avatar = avatar
        user.save()

        # Gán resident đã có sẵn cho user
        if resident:
            user.resident = resident
            user.save()

            resident_obj = Resident.objects.get(id=resident.id)
            resident_obj.user = user
            resident_obj.save()

        return user

    # def update(self, instance, validated_data):
    #     password = validated_data.pop('password', None)
    #     if password:
    #         instance.set_password(password)
    #
    #     return super().update(instance, validated_data)
