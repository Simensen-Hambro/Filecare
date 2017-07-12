from rest_framework import serializers
from rest_framework.reverse import reverse

from portal.helpers import get_branch_path
from portal.models import SharedNode, Node


class SubNodeSerializer(serializers.ModelSerializer):
    size = serializers.CharField(source='get_printable_size')
    filename = serializers.CharField(source='get_filename')
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        if obj.is_directory():
            view = 'portal:node-detail'
        else:
            view = 'portal:node-intermediate'
        return reverse(view, kwargs={'pk': obj.pk}, request=self.context.get('request'))

    class Meta:
        model = Node
        fields = ('size', 'filename', 'id', 'filename', 'directory', 'url')


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes the Node class: A file or directory with a unique UUID and some attributes.
    Also give the branch leading to the given node: the levels. 
    """
    children = SubNodeSerializer(many=True, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='portal:node-detail')
    levels = serializers.SerializerMethodField('get_node_levels')
    size = serializers.CharField(source='get_printable_size')
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = Node
        fields = ('size', 'id', 'filename', 'children', 'url', 'levels')

    def get_node_levels(self, obj):
        branch = get_branch_path(obj)
        serializer_context = {'request': self.context.get('request')}
        return SubNodeSerializer(branch, context=serializer_context, many=True).data


class ShareSubNodeSerializer(SubNodeSerializer):
    """
    Serializer for the 1st level sub-nodes of a _shared_ node. get_url reverses directories to a view with the given
       share and directory. Files are already symlinked and can be directly reversed ('/s/share/file.txt')
    """
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        share = self.context.get('share')
        url_kwargs = {
            'uuid': share.token
        }
        if obj.is_directory():
            url_kwargs['node'] = obj.id
            return reverse('portal:share-sub-node', kwargs=url_kwargs, request=self.context.get('request'))
        else:
            url_kwargs['file_path'] = share.get_child_url(obj)
            return reverse('portal:get-file', kwargs={'token': share.token,
                                                      'file_path': share.get_child_url(obj)},
                           request=self.context.get('request'))


class ShareSerializer(serializers.HyperlinkedModelSerializer):
    """
    The root level of a share. Gives the levels between the root node of a share to the current sub node. 
    Children nodes are returned as a list with ShareSubNodeSerializer (above).
    A share is created by supplying the uuid of a node, and an absolute URL to the new share is returned. 
    """
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    children = serializers.SerializerMethodField('get_relative_node', read_only=True)
    levels = serializers.SerializerMethodField('get_node_levels', read_only=True)
    node = serializers.PrimaryKeyRelatedField(many=False, write_only=True, queryset=Node.objects.all())
    url = serializers.HyperlinkedIdentityField(view_name='portal:share-root', lookup_field='token',
                                               lookup_url_kwarg='uuid', read_only=True, many=False)

    view_name = 'portal:share-root'

    class Meta:
        model = SharedNode
        fields = ('token', 'expiration', 'children', 'levels', 'user', 'node', 'url')

    def get_relative_node(self, obj):
        leaf = self.get_node_obj(obj)
        # self.node = leaf
        nodes = Node.objects.filter(parent__id=leaf.id)

        serializer_context = {'request': self.context.get('request'), 'share': obj}
        serializer = ShareSubNodeSerializer(nodes, context=serializer_context, many=True)
        return serializer.data

    def get_node_levels(self, obj):
        leaf = self.get_node_obj(obj)
        branch = get_branch_path(leaf, obj.node)
        serializer_context = {'request': self.context.get('request'),
                              'share': obj}
        serializer = ShareSubNodeSerializer(branch, context=serializer_context, many=True)
        return serializer.data

    def get_node_obj(self, obj):
        try:
            return self.node
        except AttributeError:
            node = self.context.get('node')
            try:
                self.node = Node.objects.get(id=node)
                if not obj.is_ancestor_of_node(self.node):
                    self.node = obj.node
                return self.node
            except Node.DoesNotExist:
                pass

        return obj.node

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'uuid': obj.pk,
        }
        return reverse(view_name=view_name, kwargs=url_kwargs, request=request, format=format)
