import uuid

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_delete

from app_ecommerce.models_mixins import CompressImageBeforeSaveMixin
from app_ecommerce.validators import phone_number_validator


# Create your models here.
class Base(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        str = f"{self.__class__.__name__} object '{self.title}'"
        if hasattr(self, 'parent') and self.parent is not None:
            str += f" in '{self.parent.title}'"

        return str

    def get_class_name(self):
        return self.__class__.__name__


class Goods(CompressImageBeforeSaveMixin, Base):
    def __init__(self, *args, **kwargs):
        self.image_width = 642
        self.image_name_suffix = 'goods_image'
        super().__init__(*args, **kwargs)

    title = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='title', unique=True)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/goods_images/', blank=True, null=True)
    price = models.IntegerField()
    price_prefix = models.BooleanField(default=False)
    count = models.IntegerField()
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'goods'

@receiver(post_delete, sender=Goods)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(save=False)


class Category(Base):
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='title', unique=True)

    class Meta:
        verbose_name_plural = 'categories'

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
    goods = models.ForeignKey('Goods', on_delete=models.CASCADE)

    title = models.CharField(max_length=150)
    value = models.CharField(max_length=150)


class Customer(Base):
    session_id = models.CharField(max_length=32)
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15, blank=True, null=True, validators=[phone_number_validator, ])
    last_visit = models.DateTimeField(auto_now=True)


class Order(Base):
    STATUSES = [
        ('new', 'не обработанная заявка'),
        ('active', 'в работе'),
        ('closed', 'завершено'),
        ('success_sell', 'услуга оказана'),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    goods = models.ForeignKey('Goods', on_delete=models.PROTECT, null=True)
    service = models.ForeignKey('Service', on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=12, choices=STATUSES, default=STATUSES[0][0])

    def clean(self):
        if not self.goods and not self.service:
            raise ValidationError("At least one of Goods or Service must be set")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Service(Base):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.IntegerField()
    price_prefix = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)


class Message(Base):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    text = models.TextField()

