import uuid

from django.contrib.auth.models import User
from django.db import models

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


class Goods(Base):
    title = models.CharField(max_length=150)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    price = models.IntegerField()
    count = models.IntegerField()
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'goods'


class Category(Base):
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = 'categories'


class Parameter(Base):
    uuid_key = models.UUIDField()

    title = models.CharField(max_length=150)
    value = models.CharField(max_length=150)
