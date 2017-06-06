from uuid import uuid4

from django.conf import settings
from django.db import models


class Node(models.Model):
    absolute_path = models.CharField(max_length=1000)
    parent = models.ForeignKey("Node", null=True, blank=True)
    directory = models.BooleanField(default=False)
    size = models.BigIntegerField(default=0)
    uuid = models.UUIDField(default=uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.absolute_path

    def get_relative_path(self):
        root_path = settings.ROOT_DIRECTORY
        return self.absolute_path[len(root_path):]

    def get_filename(self):
        return self.absolute_path.split("/")[-1]

    def get_printable_size(self):

        # Return in Bytes
        if self.size < 1000:
            return "{} B".format(self.size)

        # Return in KiloBytes
        elif self.size > 1000 and self.size < 1000 ** 2:
            return "{} kB".format(self.size // 1000)

        # Return in MegaBytes
        elif self.size > 1000 ** 2 and self.size < 1000 ** 3:
            return "{} MB".format(self.size // 1000 ** 2)

        # Return in GigaBytes
        elif self.size > 1000 ** 3:
            return "{0:.2f} GB".format(self.size / 1000 ** 3)
