from rest_framework import serializers

from portal.models import SharedNode, Node


class ShareSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = SharedNode
        fields = ('token', 'expiration', 'node', 'user')


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('size', 'uuid')
