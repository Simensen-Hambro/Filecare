from django.shortcuts import render
from portal.models import SharedNode
from filecare.models import Node
from django.shortcuts import get_object_or_404
import os
from django.http import Http404
from django.conf import settings


def serve_share(request, token, node_token=None):
    share = get_object_or_404(SharedNode, token=token)

    if share.node.directory is False:
        # Share is a single file
        children = [share.node]
    elif not node_token:
        # Share is a directory and no sub-node supplied
        children = Node.objects.filter(parent=share.node)
    else:
        # Share is directory and sub-node is supplied
        node = get_object_or_404(Node, uuid=node_token)
        if share.is_ancestor_of_node(node):
            children = Node.objects.filter(parent=node)
        else:
            raise Http404("Share not found")
    # Update child nodes with relative paths
    [c.set_url(share) for c in children]

    context = {
        'node': share.node,
        'children': children,
    }

    return render(request, 'filecare/index.html', context)


def get_file(request, token, file_path):
    from django.views.static import serve
    path = os.path.join(settings.ROOT_SHARE_PATH, token, file_path)
    return serve(request, os.path.basename(path), os.path.dirname(path))
