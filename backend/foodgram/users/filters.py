from rest_framework import filters

class UsersSubscriptionsFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
       
        return 