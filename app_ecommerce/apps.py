from django.apps import AppConfig

from django.utils.translation import gettext_lazy as _


class AppEcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_ecommerce'
    verbose_name = _('shop')
