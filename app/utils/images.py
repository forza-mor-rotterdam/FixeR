# thumbnailname.py

import os.path

from django.conf import settings
from django.utils import timezone


def get_date_file_path():
    return timezone.now().strftime("%Y/%m/%d")


def get_upload_path(instance, filename):
    return get_upload_path_base(filename)


def get_upload_path_base(filename):
    return os.path.join(settings.BESTANDEN_PREFIX, get_date_file_path(), filename)
