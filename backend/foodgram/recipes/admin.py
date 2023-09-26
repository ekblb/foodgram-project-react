from django.contrib import admin
from .models import Recipe, Ingredient, Tag

from import_export import resources
from import_export.admin import ImportExportModelAdmin


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource


admin.site.register(Recipe)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
