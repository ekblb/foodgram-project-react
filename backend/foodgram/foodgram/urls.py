from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/users/subscriptions/', include('users.urls'),
         name='subscriptions'),
    path('api/', include('djoser.urls'), name='users'),
    path('api/', include('recipes.urls'), name='recipes'),
    path('debug/', include('debug_toolbar.urls')),
]
