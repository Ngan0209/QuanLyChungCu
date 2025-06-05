from rest_framework.serializers import CharField, ModelSerializer, PrimaryKeyRelatedField, StringRelatedField
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
        fields = ['id', 'number','household_head','floor','price','area','create_time','update_time']
        read_only_fields = ['household_head','create_time','update_time']

class ResidentSerializer(ModelSerializer):
    apartment = PrimaryKeyRelatedField(queryset=Apartment.objects.all())
    class Meta:
        model = Resident
        fields = ['id', 'name','apartment', 'relationship_to_head','user']
        read_only_fields = ['user']

class ResidentCreateSerializer(ResidentSerializer):
    class Meta:
        model = ResidentSerializer.Meta.model
        fields = ResidentSerializer.Meta.fields + ['birthday','identity_card','gender','phone']

class ResidentDetailSerializer(ResidentSerializer):
    apartment = ApartmentSerializer(many=False)
    class Meta:
        model = ResidentSerializer.Meta.model
        fields = ResidentSerializer.Meta.fields + ['birthday', 'identity_card', 'gender', 'phone']

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
        fields = ItemSerializer.Meta.fields + ['description_item','status','received_at']

class ParkingCardSerializer(ModelSerializer):
    class Meta:
        model = ParkingCard
        fields = ['id', 'card_number','resident','visitor']

class ParkingCardDetailSerializer(ParkingCardSerializer):
    class Meta:
        model = ParkingCardSerializer.Meta.model
        fields = ParkingCardSerializer.Meta.fields + ['vehicle_type','license_plate', 'color']

class VisitorSerializer(ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id', 'full_name', 'relationship_to_resident', 'identity_card', 'phone']
        extra_kwargs = {
            'identity_card': {'required': True},
            'phone': {'required': True},
        }

class VisitorDetailSerializer(VisitorSerializer):
    parking_card = ParkingCardSerializer(many=False, read_only=True)

    class Meta:
        model = VisitorSerializer.Meta.model
        fields = VisitorSerializer.Meta.fields + ['resident','is_approved','parking_card']


class FeeTypeSerializer(ModelSerializer):
    class Meta:
        model = FeeType
        fields = ['id', 'name']

class InvoiceSerializer(ModelSerializer):
    fee_type = FeeTypeSerializer(many=False,read_only=True)
    fee_type_id = PrimaryKeyRelatedField(
        queryset=FeeType.objects.all(), source='fee_type', write_only=True
    )
    class Meta:
        model = Invoice
        fields = ['id','resident','fee_type','fee_type_id','amount', 'paid']

class InvoiceCreateSerializer(InvoiceSerializer):
    class Meta:
        model = InvoiceSerializer.Meta.model
        fields = InvoiceSerializer.Meta.fields + ['due_date']
        read_only_fields = ['paid']

    def create(self, validated_data):
        resident = validated_data.get('resident')

        # Gán apartment từ resident
        validated_data['apartment'] = resident.apartment

        return super().create(validated_data)


class InvoiceDetailSerializer(InvoiceSerializer):
    resident_name = CharField(source='resident.name', read_only=True)
    apartment_number = CharField(source='apartment.number', read_only=True)

    class Meta:
        model = InvoiceSerializer.Meta.model
        fields = InvoiceSerializer.Meta.fields + [
            'apartment_number', 'resident', 'resident_name', 'due_date'
        ]

class PaymentSerializer(ModelSerializer):
    resident = PrimaryKeyRelatedField(read_only=True)
    resident_name = CharField(source='resident.name', read_only=True)
    invoice = InvoiceSerializer(read_only=True)
    invoice_id = PrimaryKeyRelatedField(
        queryset=Invoice.objects.filter(paid=False),
        source='invoice',
        write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'resident', 'resident_name',
            'invoice', 'invoice_id',
            'method', 'proof_image', 'status',
            'create_time', 'update_time'
        ]
        read_only_fields = ['status', 'create_time', 'update_time']

    def create(self, validated_data):
        user = self.context['request'].user
        resident = getattr(user, 'resident', None)
        if not resident:
            raise ValidationError({'resident': 'User is not linked to any resident.'})
        validated_data['resident'] = resident
        return super().create(validated_data)

class ComplaintResponseSerializer(ModelSerializer):
    class Meta:
        model = ComplaintResponse
        fields = ['id', 'responder','content','create_time']
        read_only_fields = ['responder', 'create_time']

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
    choices = ChoiceSerializer(many=True)
    class Meta:
        model = Question
        fields = ['id','text', 'type', 'choices']

class SurveySerializer(ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id','title']

class SurveyDetailSerializer(SurveySerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = SurveySerializer.Meta.model
        fields = SurveySerializer.Meta.fields + ['description', 'deadline', 'questions']


class SurveyCreateSerializer(ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Survey
        fields = ['title', 'description', 'deadline', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        survey = Survey.objects.create(**validated_data)
        for question_data in questions_data:
            choices_data = question_data.pop('choices')
            question = Question.objects.create(survey=survey, **question_data)
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        return survey


class AnswerSerializer(ModelSerializer):
    choices = PrimaryKeyRelatedField(many=True, queryset=Choice.objects.all())
    class Meta:
        model = Answer
        fields = ['question','choices']

class SurveyResponseSerializer(ModelSerializer):
    answers = AnswerSerializer(many=True)
    class Meta:
        model = SurveyResponse
        fields = ['id','survey','answers']
        read_only_fields = ['survey']

    def create(self, validated_data):
        user = self.context['request'].user
        answers_data = validated_data.pop('answers')
        response = SurveyResponse.objects.create(user=user, **validated_data)

        for answer_data in answers_data:
            choices = answer_data.pop('choices')
            answer = Answer.objects.create(response=response, **answer_data)
            answer.choices.set(choices)

        return response

class AnswerDisplaySerializer(ModelSerializer):
    question = CharField(source='question.text')
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Answer
        fields = ['question', 'choices']


class SurveyResponseDisplaySerializer(ModelSerializer):
    user = StringRelatedField()
    answers = AnswerDisplaySerializer(many=True)

    class Meta:
        model = SurveyResponse
        fields = ['id', 'user', 'answers']


class UserSerializer(ModelSerializer):
    resident = PrimaryKeyRelatedField(queryset=Resident.objects.all(),
                                                  write_only=True)  # Chỉ chọn resident có sẵn

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'avatar','is_active','is_staff', 'resident']
        extra_kwargs = {'password': {'write_only': True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar'] = instance.avatar.url if instance.avatar else ''

        # Kiểm tra nếu instance có thuộc tính resident
        if hasattr(instance, 'resident'):
            data['resident'] = ResidentSerializer(instance.resident).data
        else:
            data['resident'] = None

        #chỉ có admin mới thấy được id
        request = self.context.get('request')
        if request and request.user.is_staff:
            data['id'] = instance.id
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

