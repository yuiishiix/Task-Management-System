from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializer import TaskSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    page_size = 10

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.all()

        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Search by title if provided
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        # Only show tasks created by the authenticated user
        return queryset.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        # Assign the task to the logged-in user
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        # Ensure the task is being updated by the creator
        task = self.get_object()
        if task.created_by != self.request.user:
            raise PermissionDenied("You can only update your own tasks.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure the task is being deleted by the creator
        if instance.created_by != self.request.user:
            raise PermissionDenied("You can only delete your own tasks.")
        instance.delete()


# Register View
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        if User.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


# Login View
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
