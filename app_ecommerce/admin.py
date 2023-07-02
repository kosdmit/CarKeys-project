from django.contrib import admin

from app_ecommerce.models import Goods, Category, Parameter


# Register your models here.
@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass
