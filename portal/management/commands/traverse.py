import os

from django.conf import settings
from django.core.management.base import BaseCommand
from uuid import uuid4

from portal.models import Node


class Command(BaseCommand):
    def traverse(self, node):
        """
        Function for recursively scan file structure and measure file sizes 
        """
        filesize = 0
        path = node.absolute_path

        # Loop over every file in the nodes directory
        for child_file in os.listdir(path):

            # Skip hidden files
            if child_file.startswith('.'):
                continue

            child_path = path + '/' + child_file

            # Check if child file is a directory
            if os.path.isdir(child_path):

                # If child exist, update parent_id if it has changed and mark the node as changed by adding it to changed nodes dict
                if child_path in self.nodes:
                    child_node = self.nodes[child_path]
                    if child_node.parent_id != node.id:
                        child_node.parent_id = node.id
                        self.changed_nodes[child_path] = child_node
                else:
                    # If child didn't exist, create a new Node and set parent to current node
                    child_node = Node(pk=self.next_pk, absolute_path=child_path, size=0, parent_id=node.id,
                                      directory=True)
                    self.next_pk = uuid4()
                    self.new_nodes[child_path] = child_node

                # Recursively traverse the tree by calculating filesize of the child folder
                filesize += self.traverse(child_node)
            else:

                # For child files the same thing is done as with the children directories, but a file is leaf node, so there is no recursive call.
                child_filesize = os.path.getsize(child_path)
                filesize += child_filesize

                if child_path in self.nodes:
                    self.purge_nodes.remove(child_path)
                    child_node = self.nodes[child_path]
                    if child_node.size != child_filesize or child_node.parent_id != node.id:
                        child_node.size = child_filesize
                        child_node.parent_id = node.id
                        self.changed_nodes[child_path] = child_node

                else:
                    child_node = Node(pk=self.next_pk, absolute_path=child_path, size=child_filesize, parent_id=node.id)
                    self.next_pk = uuid4()
                    self.new_nodes[child_path] = child_node

        # If the current directory has changed, update it and return the filesize
        if path in self.nodes:
            self.purge_nodes.remove(path)
            if node.size != filesize:
                node.size = filesize
                self.changed_nodes[path] = node
        else:
            node.size = filesize

        return filesize

    def handle(self, *args, **options):
        root = settings.ROOT_DIRECTORY

        # Dictionary of all existing nodes
        self.nodes = dict([(x.absolute_path, x) for x in Node.objects.all()])

        # Starts at highest PK with bulk_insert of new nodes
        self.next_pk = uuid4()

        # Set of all files that are gone from disk
        self.purge_nodes = set(self.nodes.keys())

        # Dictionary for bulk insert of new nodes and update of old nodes
        self.new_nodes = {}
        self.changed_nodes = {}

        # If root node exists, get it from dict, else create it
        if root in self.nodes:
            root_node = self.nodes[root]
        else:
            root_node = Node(pk=self.next_pk, absolute_path=root, size=0, parent_id=None, directory=True)
            self.next_pk = uuid4()
            self.new_nodes[root] = root_node

        # Traverse the file structure starting with the root node
        self.traverse(root_node)

        # Purge gone nodes
        Node.objects.filter(absolute_path__in=self.purge_nodes).delete()

        # Bulk insert new nodes
        Node.objects.bulk_create(self.new_nodes.values())

        # Update all changed nodes
        for node in self.changed_nodes.values():
            node.save()
