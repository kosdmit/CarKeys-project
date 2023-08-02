from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from app_ecommerce.models import Goods, Category, Parameter, Customer, Order, \
    Service, Message, Contact


# TODO: add action for change status for order sets
# TODO: fix image cover for empty image field in admin panel


class BaseAdminMixin:
    ordering = ('-num_id',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('meta'), {"classes": ["collapse"],
                         "fields": [("created_by", "created_date"),
                                    ("updated_by", 'updated_date')], },),
            (_('identifiers'), {"fields": [('num_id', 'uuid')],
                                "classes": ["collapse"]}),
        ]
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            'num_id', 'uuid', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.created_by:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
        obj.save()


# Register your models here.
@admin.register(Goods)
class GoodsAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'parent', 'price', 'count', 'is_active']
    list_display_links = ['title']
    list_filter = ['parent', 'is_active']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('slug')
        fieldsets += [
            (None, {"fields": ["title", "parent", "description",
                               ("image", "image_tag"),
                               ('price_prefix', 'price'),
                               ('is_active', 'count')]},),
        ]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += [
            'slug', 'image_tag'
        ]

        return readonly_fields

@admin.register(Category)
class CategoryAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'parent', 'created_date', 'updated_date']
    list_display_links = ['title']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('slug')
        fieldsets += [
            (None, {"fields": ["title", "parent"]},),
        ]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += [
            'slug',
        ]

        return readonly_fields


    def get_form(self, request, obj=None, **kwargs):
        if obj:
            form = super().get_form(request, obj, **kwargs)
            form.base_fields['parent'].queryset = Category.objects.exclude(pk=obj.pk).exclude(parent__isnull=False)
            return form
        else:
            return super().get_form(request, obj, **kwargs)

@admin.register(Parameter)
class ParameterAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'value', 'created_date', 'updated_date']
    list_display_links = ['title']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            (None, {"fields": ["title", "value", "goods"]}),
        ]

        return fieldsets


@admin.register(Contact)
class ContactAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'customer', 'num_id_customer_unique', 'name', 'phone_number']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('num_id_customer_unique')
        fieldsets += [
            (None, {"fields": ["name", "phone_number", "customer"]}),
        ]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += [
            'num_id_customer_unique',
        ]

        return readonly_fields


class ContactInlineAdmin(admin.TabularInline):
    model = Contact
    extra = 1


@admin.register(Customer)
class CustomerAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'name', 'phone_number', 'last_visit', 'session_id']
    inlines = [ContactInlineAdmin]  # TODO: add Messages, Orders inlines

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('session_id')
        fieldsets += [
            (None, {"fields": ["name", "phone_number", "last_visit"]}),
        ]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += [
            'session_id', 'last_visit',
        ]

        return readonly_fields


@admin.register(Order)
class OrderAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'customer', 'goods', 'service', 'status']
    list_display_links = ['customer']
    list_filter = ['status', 'service']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            (None, {"fields": ["customer", "goods", "service", "status"]}),
        ]

        return fieldsets

@admin.register(Service)
class ServiceAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'price', 'created_date', 'updated_date', 'is_active']
    list_display_links = ['title']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            (None, {"fields": ["title", "description", ("price_prefix", "price"), "is_active"]}),
        ]

        return fieldsets

@admin.register(Message)
class MessageAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'customer', 'text', 'created_date']
    list_display_links = ['text']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            (None, {"fields": ["customer", "text"]}),
        ]

        return fieldsets
