from rest_framework import serializers
from .models import Task, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
