from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # name = "lawyers_profile_pics/" + name
        self.delete(name)
        print("DELETED" + str(name))
        # name = "lawyers_profile_pics/" + name
        # name = name.split('lawyers_profile_pics/')[1]

        return name
