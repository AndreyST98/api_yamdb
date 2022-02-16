from rest_framework import permissions


# class IsOwnerOrReadOnly(permissions.BasePermission):

#     def has_object_permission(self, request, view, obj):
#         if obj.author.id == request.user.id \
#                 or request.method in permissions.SAFE_METHODS:
#             return True


class IsStaffIsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.author.id == request.user.id \
                or request.user.is_staff:
            return True
        return request.method in permissions.SAFE_METHODS

class IsStaffOrReadOnly(permissions.BasePermission):

     def has_object_permission(self, request, view, obj):
            if  request.user.is_staff:
                return True
