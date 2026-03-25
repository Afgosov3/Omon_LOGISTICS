from rest_framework.permissions import BasePermission


class IsAdminOnly(BasePermission):
    """Only admin users can access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsMainDispatcher(BasePermission):
    """Main dispatcher has full access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'main_dispatcher')


class IsDispatcher(BasePermission):
    """Regular dispatcher access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'dispatcher')


class IsDispatcherOrHigher(BasePermission):
    """Main dispatcher or regular dispatcher"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ['main_dispatcher', 'dispatcher']


class IsFinanceOnly(BasePermission):
    """Finance/Accountant only - Main dispatcher + Accountant"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ['main_dispatcher', 'accountant']

