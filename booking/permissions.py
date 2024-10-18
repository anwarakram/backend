from rest_framework import permissions

class IsBusinessAdminOrSystemAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['BUSINESS_ADMIN', 'SYSTEM_ADMIN']

class IsStaffOrBusinessAdminOrSystemAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['STAFF', 'BUSINESS_ADMIN', 'SYSTEM_ADMIN']