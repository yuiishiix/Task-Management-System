from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate_status(self, value):
        valid_statuses = [status[0] for status in Task.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError('Invalid status value.')
        return value

