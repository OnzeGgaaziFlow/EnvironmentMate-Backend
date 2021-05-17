from rest_framework import permissions


class OnlyCanSeeAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "list":
            if request.user.is_staff == True:
                return True
            else:
                return False
        else:
            return super().has_permission(request, view)


class OnlyCanAcceptAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            if request.user.is_staff == True:
                return True
            else:
                return False
        else:
            return super().has_permission(request, view)
