from django.contrib.auth.models import AbstractUser
from django.db import models

from dynamic_storage.models import DynamicFileField, DynamicImageField


class User(AbstractUser):
    pass


class FileModel(models.Model):
    file1 = DynamicFileField()
    file2 = DynamicFileField()


class ImageModel(models.Model):
    image1 = DynamicImageField(width_field="image1_width", height_field="image1_height")
    image1_width = models.IntegerField(editable=False)
    image1_height = models.IntegerField(editable=False)
    image2 = DynamicImageField(width_field="image2_width", height_field="image2_height")
    image2_width = models.IntegerField(editable=False)
    image2_height = models.IntegerField(editable=False)
