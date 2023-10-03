# from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, SubscriptionViewSet


router = DefaultRouter()

router.register(r'', CustomUserViewSet, basename='users')
router.register(r'subscriptions',
                SubscriptionViewSet,
                basename='subscriptions'
                )


urlpatterns = router.urls
