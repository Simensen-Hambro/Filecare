import os

from django.conf import settings
from django.core.management.base import BaseCommand

from filecare.models import Node


class Command(BaseCommand):
	help = 'Traverse '

	def handle(self, *args, **options):
		root = settings.ROOT_DIRECTORY

		# Create root node
		current_node = Node.objects.create(path=root, directory=True)

		current_level = [current_node]
		next_level = []
		while current_level:
			current_node = current_level.pop()
			for f in os.listdir(current_node.path):
				new_path = current_node.path + "/" + f
				if (os.path.isdir(new_path)):
					new_node = Node.objects.create(path=new_path, parent=current_node, directory=True)
					next_level.append(new_node)
				else:
					new_node = Node.objects.create(path=new_path, parent=current_node, directory=False)

			if not current_level:
				current_level = next_level
				next_level = []

		print("Current dir: " + str(os.getcwd()))
