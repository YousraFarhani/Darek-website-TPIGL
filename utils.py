from django.core.files.storage import default_storage

def file_cleanup(sender, **kwargs):
    path = str(kwargs['instance'].image)
    default_storage.delete(path)
