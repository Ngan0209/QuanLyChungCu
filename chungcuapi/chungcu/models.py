from tkinter.font import names
from xml.dom import ValidationErr

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Building(BaseModel):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    description = models.TextField()
    area = models.FloatField()
    total_apartment = models.FloatField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Apartment(BaseModel):
    number = models.CharField(max_length=10)
    floor = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.FloatField()
    description = models.TextField()
    area = models.FloatField()
    active = models.BooleanField(default=True)

    building = models.ForeignKey(Building, on_delete=models.CASCADE)

    def __str__(self):
        return self.number

    class Meta:
        unique_together = ['number', 'building'] #trong cùng chung cư không được trùng số căn hộ

    household_head = models.OneToOneField('Resident',on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='household_head')



class Resident(BaseModel):
    relationship_to_head = [
        ('CH', 'Chủ hộ'),
        ('VC', 'Vợ/chồng'),
        ('CT', 'Con cái'),
        ('KH', 'Khác'),
    ]
    gender = [
        ('M', 'Nam'),
        ('F', 'Nữ'),
    ]
    name = models.CharField(max_length=100)
    identity_card = models.CharField(max_length=12)
    gender = models.CharField(max_length=2, choices=gender, default=0)
    birthday = models.DateField()
    phone = models.CharField(max_length=10)
    relationship_to_head = models.CharField(max_length=2,default=1, choices=relationship_to_head)

    apartment = models.ForeignKey(Apartment,default=1, related_name='residents', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Nếu người này là chủ hộ
        if self.relationship_to_head == 'CH':

            # Kiểm tra nếu căn hộ đã có chủ
            if self.apartment.household_head and self.apartment.household_head != self:
                raise ValidationError("Căn hộ này đã có chủ hộ.")
            else:
                self.apartment.household_head = self
                self.apartment.save()


    def __str__(self):
        return self.name

class LockerItem(BaseModel):
    locker_number = models.CharField(max_length=10, unique=True,default=1)
    resident = models.OneToOneField(Resident, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=[
        ('waiting', 'Chờ nhận'),
        ('received', 'Đã nhận')
    ], default='waiting')
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.resident.name

class ParkingCard(BaseModel):
    resident = models.OneToOneField(Resident, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=10, unique=True)
    license_plate = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20, choices=[
        ('car', 'Ô tô'),
        ('motorbike', 'Xe máy'),
        ('bike', 'Xe đạp'),
        ('Other', 'Khác'),
    ])

    def __str__(self):
        return f"{self.card_number} - {self.license_plate}"

class FeeType(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Invoice(BaseModel):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
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
    #proof_image = models.ImageField(upload_to='payments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Chờ xác nhận'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    ], default='pending')





