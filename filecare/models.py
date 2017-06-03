from django.db import models
from uuid import uuid4

class Node(models.Model):

	absolute_path = models.CharField(max_length=255)
	parent = models.ForeignKey("Node", null=True, blank=True)
	directory = models.BooleanField(default=False)
	uuid = models.UUIDField(default=uuid4, editable=False)
	created = models.DateTimeField(auto_now_add=True)



	def __str__(self):
		return self.absolute_path

