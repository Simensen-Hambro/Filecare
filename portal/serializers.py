from rest_framework import serializers

from portal.models import SharedNode, Node


class NodeSerializer(serializers.ModelSerializer):
    children = serializers.StringRelatedField(many=True)

    class Meta:
        model = Node
        fields = ('size', 'id', 'children')


class ShareSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    node = NodeSerializer(many=False)

    class Meta:
        model = SharedNode
        fields = ('token', 'expiration', 'node', 'user')
