# from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RecipeViewSet,
                    TagViewSet,
                    IngredientViewSet,
                    SubscriptionViewSet,
                    # FavoriteRecipeViewSet,
                    ShoppingCartViewSet,
                    )
from users.views import CustomUserViewSet


router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
# router.register(r'recipes/{id}/favorite',
#                 FavoriteRecipeViewSet,
#                 basename='recipes_favorite'
#                 )
router.register(r'recipes/download_shopping_cart',
                ShoppingCartViewSet,
                basename='recipes_shopping_cart'
                )
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'users/subscriptions',
                SubscriptionViewSet,
                basename='subscriptions'
                )
router.register(r'sub', CustomUserViewSet, basename='users')


urlpatterns = router.urls
