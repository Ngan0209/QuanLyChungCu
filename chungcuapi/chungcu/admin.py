
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from django import forms
from .models import *
import nested_admin


class BuildingForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Building
        fields = '__all__'

class BuildingAdmin(admin.ModelAdmin):
    form = BuildingForm
    list_display = ['id', 'name', 'address','total_apartment','create_time', 'active']
    list_filter = ['name', 'address']
    search_fields = ['name','address']

class ApartmentForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Apartment
        fields = '__all__'

class ApartmentAdmin(admin.ModelAdmin):
    form = ApartmentForm
    list_display = ['id', 'number','household_head', 'building', 'active']
    list_filter = ['number', 'building', 'active']
    search_fields = ['number']

class ResidentAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'name','user__username', 'relationship_to_head', 'apartment__number']
    search_fields = ['name','apartment__number','user__username']

class LockerItemAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'locker_number', 'resident__name']
    search_fields = ['locker_number', 'resident__name']

class ItemAdmin(admin.ModelAdmin):
    list_filter = list_display =  ['id', 'name_item', 'locker_item__resident__name', 'status']
    search_fields = ['name_item', 'locker_item__resident__name']

class VisitorAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'full_name', 'resident__name','relationship_to_resident']
    search_fields = ['full_name','resident__name']

class ParkingCardAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'card_number','resident__name','visitor__full_name', 'license_plate']
    search_fields = ['card_number', 'resident__name']

class FeeTypeForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = FeeType
        fields = '__all__'

class FeeTypeAdmin(admin.ModelAdmin):
    form = FeeTypeForm
    list_filter = list_display = ['id', 'name', 'create_time']
    search_fields = ['name']

class InvoiceAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id','resident__name', 'fee_type__name','amount','paid']
    search_fields = ['resident__name','fee_type__name']

class PaymentAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'resident__name', 'invoice__fee_type__name', 'method']
    search_fields = ['resident__name', 'create_time']

class ComplaintForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Complaint
        fields = '__all__'

class ComplaintAdmin(admin.ModelAdmin):
    form = ComplaintForm
    list_filter = list_display = ['id', 'title', 'resident__name',]
    search_fields = ['resident__name', 'title']

class ComplaintResponeForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = ComplaintResponse
        fields = '__all__'

class ComplaintResponeAdmin(admin.ModelAdmin):
    form = ComplaintResponeForm
    list_filter = list_display = ['id', 'complaint__title', 'complaint__resident__name',]
    search_fields = ['complaint__resident__name', 'complaint__title']

class SurveyForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Survey
        fields = '__all__'

class ChoiceInlineAdmin(nested_admin.NestedTabularInline):
    model = Choice
    extra = 2

class QuestionInlineAdmin(nested_admin.NestedStackedInline):
    model = Question
    inlines = [ChoiceInlineAdmin]
    extra = 2

class SurveyAdmin(nested_admin.NestedModelAdmin):
    form = SurveyForm
    list_filter = list_display = ['id', 'title', 'create_time', 'deadline']
    search_fields = ['title','create_time']
    inlines = [QuestionInlineAdmin]

class SurveyResponseAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'survey__title', 'user__username']
    search_fields = ['survey__title', 'user__username']

class AnswerAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id','response__user__username','response__survey__title','choices__text']
    search_fields = ['id','id','response__user__username','response__survey__title']

class ChungCuAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản lý chung cư'



admin_site = ChungCuAppAdminSite(name='myadmin')
admin_site.register(Building, BuildingAdmin)
admin_site.register(Apartment, ApartmentAdmin)
admin_site.register(Resident, ResidentAdmin)
admin_site.register(LockerItem, LockerItemAdmin)
admin_site.register(Item, ItemAdmin)
admin_site.register(Visitor, VisitorAdmin)
admin_site.register(ParkingCard, ParkingCardAdmin)
admin_site.register(FeeType, FeeTypeAdmin)
admin_site.register(Invoice, InvoiceAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(Complaint, ComplaintAdmin)
admin_site.register(ComplaintResponse, ComplaintResponeAdmin)
admin_site.register(Survey, SurveyAdmin)
admin_site.register(SurveyResponse, SurveyResponseAdmin)
admin_site.register(Answer, AnswerAdmin)
