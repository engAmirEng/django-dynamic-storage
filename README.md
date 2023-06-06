![tox CI](https://github.com/engAmirEng/django-dynamic-storage/actions/workflows/tox.yml/badge.svg)
![PyPi Version](https://img.shields.io/pypi/v/django-dynamic-storage)
![Python Versions](https://img.shields.io/pypi/pyversions/poetry)
![Django Versions](https://img.shields.io/badge/django-2.2_|_3.0_|_3.1_|_3.2_|_4.0_|_4.1_|_4.2-green)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/engAmirEng/django-dynamic-storage/main.svg)](https://results.pre-commit.ci/latest/github/engAmirEng/django-dynamic-storage/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## django-dynamic-storage

Have you ever wanted not to store every instance of FileFileds or ImageFileds of a model in one storage or one bucket of a storage?

Now you can, because I wanted that for [my project](https://github.com/SayIfOrg/say_wagtail).

### prerequisites:

If your django version is earlier than 3.1 (<=3.0) then your database should be PostgreSQL otherwise you are good to go.

### Usage:

```plaintext
pip install django-dynamic-storage
```

in storage.py:

```python
from dynamic_storage.storage import DynamicStorageMixin

@deconstructible
class MyDynamicStorage(DynamicStorageMixin, AnyStorage):
	def init_params(self) -> dict:
		"""
		here you should return a dictionary of key value pairs that 
		later django-dynamic-storage could instantiate this class with
		"""
		return {"named_param1": self.named_param1, "named_param2": self.named_param2, ...}
```

`AnyStorage` can be a storage that you define yourself or import from [django-storages](https://pypi.org/project/django-storages/).

in models.py:

```python
from dynamic_storage.models import DynamicFileField, DynamicImageField

class MyModel(models.Model):
	"""
	DynamicFileField and DynamicImageField accept any options that django's native FileField and ImageField accept
	"""
	file = DynamicFileField()
	image = DynamicWagtailImageField()
```

Now your logic to take control of the storage where your content is going to be saved to:

```python
obj = MyModel(file=file, image=image)
obj.file.destination_storage = MyDynamicStorage(named_param1="something", named_param2="another_thing")
obj.image.destination_storage = MyDynamicStorage(named_param1="foo", named_param2="bar")
obj.save()
```

or using [signals](https://docs.djangoproject.com/en/4.2/topics/signals/):

(new to signals? learn how to [connect them](https://docs.djangoproject.com/en/4.2/topics/signals/#connecting-receiver-functions))

```python
from dynamic_storage.signals import pre_dynamic_file_save

@receiver(pre_dynamic_file_save, sender=models.MyModel)
def decide_the_storage_to_save(
instance
, field_file
, to_storage
, *args,
 **kwargs
):
    if not to_storage:
    	# destination_storage is not set, so we set it here
        field_file.destination_storage = MyDynamicStorage(named_param1="something", named_param2="another_thing")
    elif to_storage == wrong_storage:
		# override the destination_storage set earlier
		field_file.destination_storage = MyAnotherDynamicStorage(named_param1="foo", named_param2="bar")
```

#### Performance penalty?!

Not even a bit!

#### HOW?

We are just using the django's built in `JsonField` instead of `CharField`  to store more data (init\_params output) in addition to the path to the file.

so no extra queries, no extra steps, no performance penalty.