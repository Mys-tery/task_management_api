from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, filters, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import Task, Comment, Activity
from .serializers import (
    TaskSerializer,
    CommentSerializer,
    RegisterSerializer,
    UserSerializer,
    ActivitySerializer,
)
from .permissions import IsOwner


# ======================================================
# 🔹 PAGINATION
# ======================================================
class DefaultPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


# ======================================================
# 🔹 USER AUTHENTICATION (CLASS-BASED)
# ======================================================
class RegisterView(generics.CreateAPIView):
    """Register a new user."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class CustomAuthToken(ObtainAuthToken):
    """Login using token authentication."""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
        })


# ======================================================
# 🔹 USER AUTHENTICATION (FUNCTION-BASED)
# ======================================================
@api_view(['POST'])
def register_user(request):
    """Alternative registration with token return."""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'username': user.username}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    """Login and return auth token."""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# ======================================================
# 🔹 TASK VIEWS
# ======================================================
class TaskListCreateView(generics.ListCreateAPIView):
    """List all tasks or create a new one."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_completed', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        Activity.objects.create(user=self.request.user, action=f"Created task: {task.title}")


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a task."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        task = serializer.save()
        Activity.objects.create(user=self.request.user, action=f"Updated task: {task.title}")

    def perform_destroy(self, instance):
        Activity.objects.create(user=self.request.user, action=f"Deleted task: {instance.title}")
        instance.delete()


# ======================================================
# 🔹 COMMENT VIEWS
# ======================================================
class CommentListCreateView(generics.ListCreateAPIView):
    """List or create comments."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['content']

    def get_queryset(self):
        return Comment.objects.filter(task__user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        Activity.objects.create(user=self.request.user, action=f"Added comment on task ID {comment.task.id}")


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_destroy(self, instance):
        Activity.objects.create(user=self.request.user, action=f"Deleted comment ID {instance.id}")
        instance.delete()


# ======================================================
# 🔹 ACTIVITY LOG VIEWS
# ======================================================
class ActivityListView(generics.ListAPIView):
    """List user’s recent activities."""
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user).order_by('-timestamp')


# ======================================================
# 🔹 API ROOT ENDPOINT
# ======================================================
@api_view(['GET'])
def api_root(request):
    """Welcome message and endpoint list."""
    return Response({
        "message": "Welcome to the Task Management API!",
        "endpoints": {
            "register": "/api/register/",
            "login": "/api/login/",
            "tasks": "/api/tasks/",
            "comments": "/api/comments/",
            "activities": "/api/activities/"
        }
    })
