import os
from os.path import join
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from filecare.models import Node


class SharedNodeManager(models.Manager):
    def prune_expired(self):
        self.filter(expiration__lte=timezone.now()).delete()


class SharedNode(models.Model):
    token = models.UUIDField(default=uuid4, editable=False)
    created = models.DateField(auto_now=False, auto_now_add=True)
    expiration = models.DateField(auto_now=False, auto_now_add=False)

    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)

    objects = SharedNodeManager()

    def __str__(self):
        return self.token.hex

    def delete(self, *args, **kwargs):
        os.unlink(join(settings.ROOT_SHARE_PATH, str(self), os.path.basename(self.node.absolute_path)))
        os.rmdir(join(settings.ROOT_SHARE_PATH, str(self)))
        super(SharedNode, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Instance was newly created
            path = join(settings.ROOT_SHARE_PATH, str(self))

            if not os.path.isdir(path) and (self.node.directory is False):
                os.makedirs(path)

            os.symlink(self.node.absolute_path, os.path.normpath(join(settings.ROOT_SHARE_PATH, str(self),
                                                     os.path.basename(self.node.absolute_path))))
        super(SharedNode, self).save(*args, **kwargs)

    def get_child_url(self, node):
        if self.node.pk == node.pk:
            relative_path = os.path.basename(node.absolute_path)
        else:
            parent_abs_path = self.node.absolute_path
            child_abs_path = node.absolute_path
            relative_path = os.path.relpath(child_abs_path, parent_abs_path)
        return os.path.join(relative_path)

    def is_ancestor_of_node(self, potential_child):
        parent_path = self.node.absolute_path
        child_path = potential_child.absolute_path
        return os.path.commonprefix([parent_path, child_path]) is parent_path
