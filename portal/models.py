import os
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
        return f'{self.token.hex}'

    def delete(self, *args, **kwargs):
        os.unlink(f'{settings.ROOT_SHARE_PATH}/{self}/{os.path.basename(self.node.absolute_path)}')
        os.rmdir(f'{settings.ROOT_SHARE_PATH}/{self}')
        super(SharedNode, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Instance was newly created
            path = f'{settings.ROOT_SHARE_PATH}/{self}'

            if not os.path.isdir(path):
                os.makedirs(path)

            os.symlink(f'{self.node.absolute_path}',
                       f'{settings.ROOT_SHARE_PATH}/{self}/{os.path.basename(self.node.absolute_path)}')
        super(SharedNode, self).save(*args, **kwargs)

    def get_child_url(self, node):
        parent_abs_path = self.node.absolute_path
        child_abs_path = node.absolute_path
        relative_path = os.path.realpath(parent_abs_path, child_abs_path)
        return f'{os.path.join(settings.ROOT_SHARE_PATH, str(self), relative_path)}'
