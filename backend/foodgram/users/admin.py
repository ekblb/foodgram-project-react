from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', ]
    list_filter = ['id', 'email', 'username', ]
    ordering = ['id']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'user', ]
    list_filter = ['author', 'user', ]
    ordering = ['id']
