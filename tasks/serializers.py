from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import Task, Comment, Activity


# -------------------------
# USER AUTHENTICATION
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        Token.objects.create(user=user)
        return user


# -------------------------
# COMMENT SERIALIZER
# -------------------------
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


# -------------------------
# TASK SERIALIZER
# -------------------------
class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    # This prepares for filtering
    def validate_priority(self, value):
        valid_priorities = ['Low', 'Medium', 'High']
        if value not in valid_priorities:
            raise serializers.ValidationError("Priority must be Low, Medium, or High.")
        return value


# -------------------------
# ACTIVITY SERIALIZER
# -------------------------
class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    task = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ['timestamp']
