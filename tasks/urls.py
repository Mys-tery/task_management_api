from django.urls import path
from .views import (
    api_root,
    RegisterView,
    CustomAuthToken,
    register_user,
    login_user,
    TaskListCreateView,
    TaskDetailView,
    CommentListCreateView,
    CommentDetailView,
    ActivityListView,
)

urlpatterns = [
    # ------------------------------------------------
    #  ROOT ENDPOINT
    # ------------------------------------------------
    path('', api_root, name='api-root'),

    # ------------------------------------------------
    #  AUTHENTICATION
    # ------------------------------------------------
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),

    # Optional: function-based versions
    path('auth/register/', register_user, name='register-user'),
    path('auth/login/', login_user, name='login-user'),

    # ------------------------------------------------
    #  TASKS
    # ------------------------------------------------
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # ------------------------------------------------
    #  COMMENTS
    # ------------------------------------------------
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

    # ------------------------------------------------
    #  ACTIVITY LOG
    # ------------------------------------------------
    path('activities/', ActivityListView.as_view(), name='activity-list'),
]
