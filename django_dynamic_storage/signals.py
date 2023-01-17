from django.dispatch import Signal


# provides args: instance, field_file, to_storage
pre_dynamic_file_save = Signal()
