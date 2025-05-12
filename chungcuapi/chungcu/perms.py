from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsResidentUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.is_staff

class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Admin luôn có quyền
        if request.user.is_staff:
            return True

        # Nếu obj có trường user → so sánh trực tiếp
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Nếu obj có resident → so sánh resident.user
        if hasattr(obj, 'resident') and hasattr(obj.resident, 'user'):
            return obj.resident.user == request.user

        return False

class IsResidentOfApartment(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff:
            return True

        # Trường hợp đối tượng là Apartment → kiểm tra resident của căn hộ
        if hasattr(obj, 'residents'):
            return obj.residents.filter(user=user).exists()

        # Trường hợp đối tượng có thuộc tính apartment → đi qua resident của apartment
        if hasattr(obj, 'apartment') and hasattr(obj.apartment, 'residents'):
            return obj.apartment.residents.filter(user=user).exists()

        return False