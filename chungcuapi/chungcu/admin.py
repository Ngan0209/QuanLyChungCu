from django.contrib import admin
from .models import Building, Apartment, Resident, LockerItem, ParkingCard, FeeType, Invoice, Payment

class BuildingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address','total_apartment','create_time', 'active']
    list_filter = ['name', 'create_time']
    search_fields = ['name','address']

class ApartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'number','household_head', 'building', 'active']
    search_fields = ['number']

class ResidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'relationship_to_head', 'apartment']
    search_fields = ['name']

class LockerItemAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'locker_number', 'resident__name',  'status']
    search_fields = ['locker_number', 'resident__name']

class ParkingCardAdmin(admin.ModelAdmin):
    list_filter = list_display = ['id', 'card_number','resident__name', 'license_plate']
    search_fields = ['card_number', 'resident__name']

class ChungCuAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản lý chung cư'



admin_site = ChungCuAppAdminSite(name='myadmin')
admin_site.register(Building, BuildingAdmin)
admin_site.register(Apartment, ApartmentAdmin)
admin_site.register(Resident, ResidentAdmin)
admin_site.register(LockerItem, LockerItemAdmin)
admin_site.register(ParkingCard, ParkingCardAdmin)
admin_site.register(FeeType)
admin_site.register(Invoice)
admin_site.register(Payment)
