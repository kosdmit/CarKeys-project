import uuid

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete

from app_ecommerce.models_mixins import CompressImageBeforeSaveMixin


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


class Goods(CompressImageBeforeSaveMixin, Base):
    def __init__(self, *args, **kwargs):
        self.image_width = 642
        self.image_name_suffix = 'goods_image'
        super().__init__(*args, **kwargs)

    title = models.CharField(max_length=150)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/goods_images/', blank=True, null=True)
    price = models.IntegerField()
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

    class Meta:
        verbose_name_plural = 'categories'


class Parameter(Base):
    uuid_key = models.UUIDField()

    title = models.CharField(max_length=150)
    value = models.CharField(max_length=150)
