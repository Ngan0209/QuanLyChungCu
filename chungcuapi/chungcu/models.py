
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField

AbstractUser.username.field.error_messages['unique'] = 'Tên đăng nhập đã tồn tại'
class User(AbstractUser):
    avatar = CloudinaryField('avatar',null = True, )

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-id']

class Building(BaseModel):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    description = RichTextField(null=True, blank=True)
    area = models.FloatField()
    total_apartment = models.FloatField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Apartment(BaseModel):
    number = models.CharField(max_length=10)
    floor = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.FloatField()
    description = RichTextField(null=True, blank=True)
    area = models.DecimalField(max_digits=6, decimal_places=2)
    active = models.BooleanField(default=True)

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='apartments', default=1)

    def __str__(self):
        return self.number

    class Meta:
        unique_together = ['number', 'building'] #trong cùng chung cư không được trùng số căn hộ

    household_head = models.OneToOneField('Resident',on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='household_head')



class Resident(BaseModel):
    relationship_to_head = [
        ('owner', 'Chủ hộ'),
        ('wife/husband', 'Vợ/Chồng'),
        ('child', 'Con cái'),
        ('parent', 'Cha/Mẹ'),
        ('other', 'Khác')
    ]
    gender = [
        ('Male', 'Nam'),
        ('Female', 'Nữ'),
    ]

    name = models.CharField(max_length=100)
    identity_card = models.CharField(max_length=12, unique=True)
    gender = models.CharField(max_length=6, choices=gender, default=0)
    birthday = models.DateField()
    phone = models.CharField(max_length=10)
    relationship_to_head = models.CharField(max_length=12,default=1, choices=relationship_to_head)
    active = models.BooleanField(default=True)

    user = models.OneToOneField('User', on_delete=models.CASCADE, null=True, blank=True)
    apartment = models.ForeignKey(Apartment,default=1, related_name='residents', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Nếu người này là chủ hộ
        if self.relationship_to_head == 'owner':

            # Kiểm tra nếu căn hộ đã có chủ
            if self.apartment.household_head and self.apartment.household_head != self:
                raise ValidationError("Căn hộ này đã có chủ hộ.")
            else:
                self.apartment.household_head = self
                self.apartment.save()


    def __str__(self):
        return self.name

class LockerItem(BaseModel):
    locker_number = models.CharField(max_length=10,default=1)
    resident = models.OneToOneField(Resident, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.locker_number} - {self.resident.name}"

class Item(BaseModel):
    locker_item = models.ForeignKey(LockerItem, on_delete=models.CASCADE, related_name='items')
    name_item = models.CharField(max_length=100)
    description_item = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('waiting', 'Chờ nhận'),
        ('received', 'Đã nhận')
    ], default='waiting')
    received_at = models.DateTimeField(null=True, blank=True)

class Visitor(BaseModel):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    identity_card = models.CharField(max_length=12, unique=True)
    phone = models.CharField(max_length=10, default=0)
    relationship_to_resident = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name

    is_approved = models.BooleanField(default=False)

class ParkingCard(BaseModel):
    resident = models.OneToOneField(Resident, on_delete=models.CASCADE, null=True, blank=True)
    visitor = models.OneToOneField(Visitor, on_delete=models.CASCADE, null=True, blank=True, related_name='parking_card')
    card_number = models.CharField(max_length=10, unique=True)
    license_plate = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20, choices=[
        ('car', 'Ô tô'),
        ('motorbike', 'Xe máy'),
        ('bike', 'Xe đạp'),
        ('Other', 'Khác'),
    ])
    color = models.CharField(max_length=20,default='Trắng')

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.resident and not self.visitor:
            raise ValidationError('Thẻ phải thuộc về cư dân hoặc người thân.')
        if self.resident and self.visitor:
            raise ValidationError('Chỉ được gán thẻ cho 1 trong 2: cư dân hoặc người thân.')

    def __str__(self):
        return f"{self.card_number} - {self.license_plate}"

class FeeType(BaseModel):
    name = models.CharField(max_length=100)
    description = RichTextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Invoice(BaseModel):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='invoices', default=1)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='invoices')
    fee_type = models.OneToOneField(FeeType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.resident.name} - {self.fee_type.name}"


class Payment(BaseModel):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=[
        ('momo', 'Momo'),
        ('vnpay', 'VNPay')
    ])
    proof_image = CloudinaryField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Chờ xác nhận'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    ], default='pending')

    def __str__(self):
        return f"{self.resident.name} - {self.invoice.id}"


class Complaint(BaseModel):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Chờ xử lý'),
        ('resolved', 'Đã xử lý'),
    ], default='pending', )
    is_resolved = models.BooleanField(default=False,)

    def __str__(self):
        return f"{self.resident.name} - {self.title}"

class ComplaintResponse(BaseModel):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="responses")
    responder = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    content = RichTextField()

    def __str__(self):
        return f"Phản hồi bởi {self.responder.username} - {self.complaint}"

class Survey(BaseModel):
    title = models.CharField(max_length=255)
    description = RichTextField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title


class Question(BaseModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    QUESTION_TYPES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
    )
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single')
    def __str__(self):
        return f"{self.survey.title} - {self.text}"

class Choice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=1, related_name= 'choices')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class SurveyResponse(BaseModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_responses', default=1)
    def __str__(self):
        return f"{self.user.username} - {self.survey.title}"

class Answer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f"{self.response.survey.title} - {self.question} - {self.choices}"



