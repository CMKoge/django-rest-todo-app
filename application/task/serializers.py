from rest_framework import serializers
from .models import Task


class TaskCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ["title", "description", "state"]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace.")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "state"]
        read_only_fields = []

    def validate_title(self, value):
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "state", "created_at", "timestamp"]


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "state", "created_at", "timestamp"]
