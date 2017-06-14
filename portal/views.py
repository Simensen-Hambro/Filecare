import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from portal.models import SharedNode, Node

from rest_framework.views import APIView
from portal.serializers import NodeSerializer, ShareSerializer
from rest_framework.response import Response
from rest_framework import status


def get_path(node, stop_parent=None, share=None):
    links = []
    if stop_parent is not None and (node.pk is stop_parent.pk):
        node.set_url(share)
        links.append({'name': 'Root', 'url': node.url})
        return links

    if node.parent:
        parent = node
        while parent:
            parent.set_url(share)
            if parent.parent:
                links.append({'name': parent.get_filename(), 'url': parent.url})
                parent = parent.parent
            else:
                links.append({'name': 'Root', 'url': parent.url})
                break

    else:
        links.append({'name': 'Root', 'uuid': node.id})
    links.reverse()
    return links


def get_file(request, token, file_path):
    from django.views.static import serve
    path = os.path.join(settings.ROOT_SHARE_PATH, token, file_path)
    return serve(request, os.path.basename(path), os.path.dirname(path))

@login_required()
def root(request):
    return admin_browse(request, None)


@login_required()
def admin_browse(request, node_uuid=None):
    if node_uuid is None:
        node = Node.objects.get(parent__isnull=True)
    else:
        node = get_object_or_404(Node, id=node_uuid)
    links = get_path(node)
    children = Node.objects.filter(parent=node)

    # Update child nodes with relative paths
    [c.set_url(None) for c in children]
    context = {
        'links': links,
        'children': children,
    }
    return render(request, 'filecare/browse.html', context=context)


def browse_share(request, token, node_uuid=None):
    share = get_object_or_404(SharedNode, token=token)
    node = share.node
    if node_uuid:
        node = get_object_or_404(Node, id=node_uuid)
        if not share.is_ancestor_of_node(node):
            raise Http404

    if node.directory is False:
        children = [node]
    else:
        children = Node.objects.filter(parent=node)

    links = get_path(node, stop_parent=share.node, share=share)

    # Update child nodes with relative paths
    [c.set_url(share) for c in children]

    context = {
        'share': share,
        'node': share.node,
        'children': children,
        'links': links,
    }

    return render(request, 'filecare/index.html', context)


class ShareDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, uuid):
        try:
            return SharedNode.objects.get(token=uuid)
        except SharedNode.DoesNotExist:
            raise Http404

    def get(self, request, uuid, format=None):
        share = self.get_object(uuid)
        serializer = ShareSerializer(share)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShareList(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def post(self, request, format=None):
        serializer = ShareSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
