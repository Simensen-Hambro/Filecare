import os
from datetime import timedelta as dt
from os.path import join
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone as tz

DEFAULT_EXPIRATION = 1  # Days into the future


class SharedNodeManager(models.Manager):
    def prune_expired(self):
        self.filter(expiration__lte=tz.now()).delete()


class Node(models.Model):
    absolute_path = models.CharField(max_length=1000)
    parent = models.ForeignKey("Node", null=True, blank=True, related_name='children')
    directory = models.BooleanField(default=False)
    size = models.BigIntegerField(default=0)
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
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
        return os.path.basename(self.absolute_path)

    def get_file_type(self):
        # https://stackoverflow.com/a/678242
        return os.path.splitext(self.get_filename())[1][1:]

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

    def set_url1(self, share=None):
        if share is None:
            self.url = reverse('portal:node-detail',
                               kwargs={'pk': self.id})
        else:
            if self.directory:
                self.url = reverse('portal:share-sub-node',
                                   kwargs={'uuid': share.token,
                                           'node': self.id})
            elif not self.directory:
                self.url = reverse('portal:get-file',
                                   kwargs={'token': share.token,
                                           'file_path': share.get_child_url(self)})
        return self.url

    def is_directory(self):
        return self.directory


def default_expiration_date():
    return tz.now() + dt(days=DEFAULT_EXPIRATION)


class SharedNode(models.Model):
    token = models.UUIDField(default=uuid4, editable=False)
    created = models.DateField(auto_now=False, auto_now_add=True)
    expiration = models.DateTimeField(auto_now=False, auto_now_add=False, default=default_expiration_date)

    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)

    objects = SharedNodeManager()

    def __str__(self):
        return str(self.token)

    def delete(self, *args, **kwargs):
        os.unlink(join(settings.ROOT_SHARE_PATH, str(self), os.path.basename(self.node.absolute_path)))
        os.rmdir(join(settings.ROOT_SHARE_PATH, str(self)))
        super(SharedNode, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Instance was newly created
            path = join(settings.ROOT_SHARE_PATH, str(self))

            if not os.path.isdir(path):
                os.makedirs(path)

            os.symlink(self.node.absolute_path, os.path.normpath(join(settings.ROOT_SHARE_PATH, str(self),
                                                                      os.path.basename(self.node.absolute_path))))
        super(SharedNode, self).save(*args, **kwargs)

    def get_child_url(self, node):
        if self.node.pk == node.pk:
            parent_abs_path = os.path.basename(node.absolute_path)
            relative_path = ''
        else:
            parent_abs_path = self.node.absolute_path
            child_abs_path = node.absolute_path
            relative_path = os.path.relpath(child_abs_path, parent_abs_path)
        return os.path.join(os.path.basename(parent_abs_path), relative_path) # :-1]

    def is_ancestor_of_node(self, potential_child):
        parent_path = self.node.absolute_path
        child_path = potential_child.absolute_path
        return os.path.commonprefix([parent_path, child_path]) is parent_path
