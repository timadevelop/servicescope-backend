from django.conf import settings

import importlib

def load(path):
    parts = path.split('.')
    class_name = parts.pop()
    module_name = '.'.join(parts)
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_

DEFAULT_PERMISSION_CLASSES = list(map(load, settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']))