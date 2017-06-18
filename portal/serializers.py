from rest_framework import serializers

from portal.helpers import get_branch_path
from portal.models import SharedNode, Node


class SubNodeSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_abs_url')

    def get_abs_url(self, obj):
        share = self.context.get('share')
        return obj.set_url(share)

    class Meta:
        model = Node
        fields = ('size', 'id', 'get_filename', 'directory', 'url', 'get_file_type')


class NodeSerializer(serializers.ModelSerializer):
    children = SubNodeSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField('get_rep_url')
    levels = serializers.SerializerMethodField('get_node_levels')

    class Meta:
        model = Node
        fields = ('size', 'id', 'get_filename', 'children', 'url', 'levels')

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


class ShareSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    # node = NodeSerializer(many=False, read_only=True)
    node = serializers.SerializerMethodField('get_relative_node')
    levels = serializers.SerializerMethodField('get_node_levels', read_only=True)

    class Meta:
        model = SharedNode
        fields = ('token', 'expiration', 'node', 'levels', 'user')

    def get_relative_node(self, obj):
        node = self.context.get('node')
        try:
            parent = Node.objects.get(id=node)
            self.node = parent
            if not obj.is_ancestor_of_node(parent):
                nodes = [obj.node]
            nodes = Node.objects.filter(parent__id=node)
        except Node.DoesNotExist:
            nodes = [obj.node]



        serializer_context = {'request': None, 'share': obj}
        serializer = SubNodeSerializer(nodes, context=serializer_context, many=True)
        return serializer.data

    def get_node_levels(self, obj):
        # TODO: Refactor code from get_relative_node so we dont do any repeating queries
        branch = get_branch_path(self.node, obj)
        serializer_context = {'request': self.context.get('request'),
                              'share': obj}
        serializer = SubNodeSerializer(branch, context=serializer_context, many=True)
        return serializer.data
