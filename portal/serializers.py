from rest_framework import serializers
from rest_framework.reverse import reverse

from portal.helpers import get_branch_path
from portal.models import SharedNode, Node


class SubNodeSerializer(serializers.HyperlinkedModelSerializer):
    size = serializers.CharField(source='get_printable_size')
    filename = serializers.CharField(source='get_filename')
    url = serializers.HyperlinkedIdentityField(view_name='portal:node-detail')

    class Meta:
        model = Node
        fields = ('size', 'filename', 'id', 'filename', 'directory', 'url')
        view_name = 'kek'


class NodeSerializer(serializers.HyperlinkedModelSerializer):
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
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        url_kwargs = {
            'uuid': self.context.get('share').token,
            'node': obj.id
        }
        return reverse('portal:share-sub-node', kwargs=url_kwargs, request=self.context.get('request'))


class ShareSerializer(serializers.HyperlinkedModelSerializer):
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
