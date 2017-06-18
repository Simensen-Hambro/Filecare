from rest_framework import serializers

from portal.models import SharedNode, Node


class SubNodeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='portal:node-detail')

    class Meta:
        model = Node
        fields = ('size', 'id', 'get_filename', 'directory', 'url')


class NodeSerializer(serializers.ModelSerializer):
    children = SubNodeSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField('get_rep_url')

    class Meta:
        model = Node
        fields = ('size', 'id', 'get_filename', 'children', 'url')

    def get_rep_url(self, obj):
        share = self.context.get('share')
        return obj.set_url(share)


class ShareSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    # node = NodeSerializer(many=False, read_only=True)
    node = serializers.SerializerMethodField('get_relative_node')

    class Meta:
        model = SharedNode
        fields = ('token', 'expiration', 'node', 'user')

    def get_relative_node(self, obj):
        node = self.context.get('node')
        if node is None:
            node = obj.node
        else:
            try:
                node = Node.objects.get(id=node)
            except Node.DoesNotExist:
                node = None

        if not obj.is_ancestor_of_node(node):
            return None

        serializer_context = {'request': self.context.get('request'),
                              'share': obj}
        serializer = SubNodeSerializer(node, context=serializer_context)
        return serializer.data
