# from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RecipeViewSet,
                    TagViewSet,
                    IngredientViewSet,
                    # FavoriteRecipeViewSet,
                    )


router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
# router.register(r'recipes/shopping_cart',
#                 RecipeViewSet,
#                 basename='recipes_shopping_cart'
#                 )
# router.register(r'recipes/{id}/favorite',
#                 FavoriteRecipeViewSet,
#                 basename='recipes_favorite'
#                 )
# router.register(r'recipes/download_shopping_cart',
#                 ShoppingCartViewSet,
#                 basename='recipes_shopping_cart'
#                 )

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = router.urls
