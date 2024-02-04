from rest_framework import permissions


class IsDelivery(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery crew').exists()

# Only manager permission
class IsManager(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
