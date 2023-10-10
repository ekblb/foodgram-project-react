# from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet


router = DefaultRouter()

router.register(r'', SubscriptionViewSet, basename='subscriptions',)


urlpatterns = router.urls
