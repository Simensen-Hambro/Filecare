import os

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import (ListAPIView)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from portal.models import SharedNode, Node
from portal.serializers import ShareSerializer, NodeSerializer


def get_file(request, token, file_path):
    from django.views.static import serve
    path = os.path.join(settings.ROOT_SHARE_PATH, token, file_path)
    return serve(request, os.path.basename(path), os.path.dirname(path))


@permission_classes((IsAuthenticatedOrReadOnly,))
class ShareDetail(APIView):
    """
    Retrieve, update or delete a Share instance.
    """

    def get_object(self, uuid, node=None):
        try:
            return SharedNode.objects.get(token=uuid)
        except SharedNode.DoesNotExist:
            raise Http404

    def get(self, request, uuid=None, node=None, format=None):
        try:
            share = self.get_object(uuid)
            serializer = ShareSerializer(share, context={'node': node, 'request': request})
            return Response(serializer.data)
        except SharedNode.DoesNotExist:
            return None

    def delete(self, request, uuid, format=None, node=None):
        share = self.get_object(uuid)
        share.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format=None):
        serializer = ShareSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeListAPIView(ListAPIView):
    queryset = Node.objects.filter(parent__isnull=True)
    serializer_class = NodeSerializer


class NodeDetail(mixins.RetrieveModelMixin,
                 generics.GenericAPIView):
    queryset = Node.objects.all().order_by('get_filename')
    serializer_class = NodeSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            instance = Node.objects.get(parent__isnull=True)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        r = super().retrieve(request, *args, **kwargs)
        return r


class PreDownloadNode(APIView):
    def get(self, request, pk, format=None):
        node = Node.objects.get(pk=pk)
        if not node.is_directory():
            share = SharedNode.objects.create(node=node, user=request.user)
            return redirect(reverse('portal:get-file',
                                    kwargs={'token': share.token,
                                            'file_path': share.get_child_url(node)}))
