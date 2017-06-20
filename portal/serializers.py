from rest_framework import serializers

from portal.helpers import get_branch_path
from portal.models import SharedNode, Node
from rest_framework.reverse import reverse


class SubNodeSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_abs_url')
    size = serializers.CharField(source='get_printable_size')
    filename = serializers.CharField(source='get_filename')

    def get_abs_url(self, obj):
        share = self.context.get('share')
        return obj.set_url(share)

    class Meta:
        model = Node
        fields = ('size', 'id', 'filename', 'directory', 'url')


class NodeSerializer(serializers.ModelSerializer):
    children = SubNodeSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField('get_rep_url')
    levels = serializers.SerializerMethodField('get_node_levels')
    size = serializers.CharField(source='get_printable_size')
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = Node
        fields = ('size', 'id', 'filename', 'children', 'url', 'levels')

    def get_rep_url(self, obj):
        share = self.context.get('share')
        return obj.set_url(share)

    def get_node_levels(self, obj):
        # TODO: Refactor code from get_relative_node so we dont do any repeating queries
        branch = get_branch_path(obj)
        share = self.context.get('share')
        serializer_context = {'request': self.context.get('request'),
                              'share': share}
        serializer = SubNodeSerializer(branch, context=serializer_context, many=True)
        return serializer.data


class ShareSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    # node = NodeSerializer(many=False, read_only=True)
    children = serializers.SerializerMethodField('get_relative_node', read_only=True)
    levels = serializers.SerializerMethodField('get_node_levels', read_only=True)
    node = serializers.PrimaryKeyRelatedField(many=False, write_only=True, queryset=Node.objects.all())
    url = serializers.HyperlinkedIdentityField(view_name='portal:share-root', lookup_field='token', lookup_url_kwarg='uuid', read_only=True, many=False)

    view_name = 'root-share'


    class Meta:
        model = SharedNode
        fields = ('token', 'expiration', 'children', 'levels', 'user', 'node', 'url')

    def get_relative_node(self, obj):
        leaf = self.get_node_obj(obj)
        #self.node = leaf
        nodes = Node.objects.filter(parent__id=leaf.id)

        serializer_context = {'request': None, 'share': obj}
        serializer = SubNodeSerializer(nodes, context=serializer_context, many=True)
        return serializer.data

    def get_node_levels(self, obj):
        # TODO: Refactor code from get_relative_node so we dont do any repeating queries
        leaf = self.get_node_obj(obj)
        branch = get_branch_path(leaf, obj.node, obj)
        serializer_context = {'request': self.context.get('request'),
                              'share': obj}
        serializer = SubNodeSerializer(branch, context=serializer_context, many=True)
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
        return reverse('root-share', kwargs=url_kwargs, request=request, format=format)
