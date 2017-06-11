from uuid import uuid4

from django.conf import settings
from django.db import models
from django.urls import reverse


class Node(models.Model):
    absolute_path = models.CharField(max_length=1000)
    parent = models.ForeignKey("Node", null=True, blank=True)
    directory = models.BooleanField(default=False)
    size = models.BigIntegerField(default=0)
    uuid = models.UUIDField(default=uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.absolute_path

    def get_file_type(self):
        if self.directory:
            return 'dir'
        else:
            return self.absolute_path.split(".")[-1]

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

    def set_url(self, share=None):
        if share is None:
            self.url = reverse('portal:admin-browse-node', kwargs={'node_uuid': self.uuid.hex})
        else:
            if self.directory:
                self.url = reverse('portal:show-sub-share',
                                   kwargs={'token': share.token.hex, 'node_uuid': self.uuid.hex})
            elif not self.directory:
                self.url = reverse('portal:get-file',
                                   kwargs={'token': share.token.hex, 'file_path': share.get_child_url(self)})
