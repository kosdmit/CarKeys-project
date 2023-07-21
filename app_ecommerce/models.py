import uuid

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, AutoField
from django.db.models.fields import checks
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from app_ecommerce.models_mixins import CompressImageBeforeSaveMixin
from app_ecommerce.validators import phone_number_validator


# Create your models here.
class Base(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4,
                            unique=True, verbose_name=_('unique identifier'))
    num_id = models.IntegerField(unique=True, editable=False, verbose_name=_('#'))

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('created by'), editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('updated by'), editable=False,
                                   related_name='+')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date of creation'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('date of updating'))

    class Meta:
        abstract = True

    def get_class_name(self):
        return self.__class__.__name__

    def save(self, *args, **kwargs):
        if not self.num_id:
            max_id = self.__class__.objects.all().aggregate(max_id=models.Max('num_id'))['max_id']
            if max_id is not None:
                self.num_id = max_id + 1
            else:
                self.num_id = 1
        super().save(*args, **kwargs)


class Goods(CompressImageBeforeSaveMixin, Base):
    def __init__(self, *args, **kwargs):
        self.image_width = 642
        self.image_name_suffix = 'goods_image'
        super().__init__(*args, **kwargs)

    title = models.CharField(max_length=150, verbose_name=_('title'))
    slug = AutoSlugField(populate_from='title', unique=True)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True,
                               blank=True, verbose_name=_('category'))
    description = models.TextField(verbose_name=_('description'))
    image = models.ImageField(upload_to='images/goods_images/', blank=True, null=True,
                              verbose_name=_('image'))
    price = models.IntegerField(verbose_name=_('price'))
    price_prefix = models.BooleanField(default=False, verbose_name=_('price prefix'))
    count = models.IntegerField(verbose_name=_('count'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))

    class Meta:
        verbose_name = pgettext_lazy('singular', 'goods')
        verbose_name_plural = pgettext_lazy('plural', 'goods')

    def __str__(self):
        return self.title

@receiver(post_delete, sender=Goods)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(save=False)


class Category(Base):
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True,
                               blank=True, verbose_name=_('parent category'))
    title = models.CharField(max_length=150, verbose_name=_('title'))
    slug = AutoSlugField(populate_from='title', unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        if self.parent:
            return f'Подкатегория "{self.title}" в категории "{self.parent.title}"'
        else:
            return f'Категория "{self.title}"'

    def clean(self):
        # checking parent category is a top level category
        if self.parent and self.parent.parent:
            raise ValidationError("Parent category must be a top level category.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_goods(self):
        child_categories = Category.objects.filter(parent=self)
        goods = Goods.objects.filter(Q(parent=self) | Q(parent__in=child_categories))

        return goods


class Parameter(Base):
    goods = models.ManyToManyField('Goods', verbose_name=_('goods'))

    title = models.CharField(max_length=150, verbose_name=_('title'))
    value = models.CharField(max_length=150, verbose_name=_('value'))

    class Meta:
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')


class Customer(Base):
    session_id = models.CharField(max_length=32, verbose_name=_('session'))
    name = models.CharField(max_length=150, verbose_name=_('name'))
    phone_number = models.CharField(max_length=15, blank=True, null=True,
                                    validators=[phone_number_validator, ], verbose_name=_('phone number'))
    last_visit = models.DateTimeField(auto_now=True, verbose_name=_('last visit'))

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        name = self.name if self.name else _('unknown')
        number = _('#') + str(self.num_id)
        return str(_('customer')).title() + ' ' + number + ' - ' + name.title()


class Order(Base):
    STATUSES = [
        ('new', 'не обработанная заявка'),
        ('active', 'в работе'),
        ('closed', 'завершено'),
        ('success_sell', 'услуга оказана'),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name=_('customer'))
    goods = models.ForeignKey('Goods', on_delete=models.PROTECT, null=True, verbose_name=_('goods'))
    service = models.ForeignKey('Service', on_delete=models.PROTECT, null=True, verbose_name=_('service'))
    status = models.CharField(max_length=12, choices=STATUSES, default=STATUSES[0][0], verbose_name=_('status'))

    def clean(self):
        if not self.goods and not self.service:
            raise ValidationError("At least one of Goods or Service must be set")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        customer = self.customer.__str__()
        number = _('#') + str(self.num_id)
        return _('The order ') + number + _(' from ') + customer


class Service(Base):
    title = models.CharField(max_length=150, verbose_name=_('title'))
    description = models.TextField(verbose_name=_('description'))
    price = models.IntegerField(verbose_name=_('price'))
    price_prefix = models.BooleanField(default=False, verbose_name=_('price prefix'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')

    def __str__(self):
        return self.title


class Message(Base):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name=_('customer'))
    text = models.TextField(verbose_name=_('text'))

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')

