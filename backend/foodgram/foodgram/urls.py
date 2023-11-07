from django.contrib import admin
from django.urls import include, path
# from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
# from rest_framework.routers import DefaultRouter
# from users.views import CustomUserViewSet

# router = DefaultRouter()

# router.register('recipes', RecipeViewSet, basename='recipes')
# router.register('tags', TagViewSet, basename='tags')
# router.register('ingredients', IngredientViewSet, basename='ingredients')
# router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('recipes.urls.py')),
    path('api/', include('users.urls.py')),
    path('debug/', include('debug_toolbar.urls')),
]
