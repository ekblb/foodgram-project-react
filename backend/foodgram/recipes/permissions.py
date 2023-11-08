from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.author == request.user
