"""
Custom permissions for ONG ADJAHI Platform
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for authenticated users, write for admins only"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsMedicalStaff(permissions.BasePermission):
    """Allow access only to medical staff (doctors, midwives, nurses, psychologists)"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_medical_staff
        )


class CanManagePatients(permissions.BasePermission):
    """Allow access to users who can manage patients"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_manage_patients
        )


class CanCreateCPN(permissions.BasePermission):
    """Allow CPN creation only to midwives and doctors"""
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            return (
                request.user and
                request.user.is_authenticated and
                request.user.can_create_cpn
            )
        return request.user and request.user.is_authenticated
