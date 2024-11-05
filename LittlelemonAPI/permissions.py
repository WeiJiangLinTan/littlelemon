from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name="Manager"):
            return True
        return False
    
class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Delivery crew'):
            return True
        return False