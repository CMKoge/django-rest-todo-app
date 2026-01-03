from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Task
from .serializers import (
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskListSerializer,
    TaskDetailSerializer,
)
from .utils import add  # Example utility function

# Create task
@api_view(["POST"])
def create_task(request):
    print("Request data:", request.data)
    serializer = TaskCreateSerializer(data=request.data)
    print("Serializer:", serializer)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            task = serializer.save()
            output = TaskDetailSerializer(task)
            print("Created Task:", output.data)
            return Response(output.data, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response(
            {"detail": "Database error occurred while creating task."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# List all tasks
@api_view(["GET"])
def list_tasks(request):
    qs = Task.objects.all().order_by("-created_at")
    serializer = TaskListSerializer(qs, many=True)
    add.delay(4, 6)  # Example of calling a Celery task
    return Response(serializer.data, status=status.HTTP_200_OK)


# Retrieve single task by id
@api_view(["GET"])
def retrieve_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update task (PUT - full, PATCH - partial)
@api_view(["PUT"])
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            updated = serializer.save()
            return Response(TaskDetailSerializer(updated).data, status=status.HTTP_200_OK)
    except IntegrityError:
        return Response({"detail": "Database integrity error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Delete task
@api_view(["DELETE"])
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    try:
        with transaction.atomic():
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except IntegrityError:
        return Response({"detail": "Database integrity error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Dedicated change state endpoint
@api_view(["POST"])
def change_task_state(request, pk):
    """
    POST payload: {"state": "DONE"}  (must be one of the choices)
    This endpoint only updates the state field.
    """
    task = get_object_or_404(Task, pk=pk)
    state = request.data.get("state")
    if state is None:
        return Response({"state": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

    # simple validation against model choices
    valid_states = {choice[0] for choice in Task.State.choices}
    if state not in valid_states:
        return Response({"state": ["Invalid state."]}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            task.state = state
            task.save()
            return Response(TaskDetailSerializer(task).data, status=status.HTTP_200_OK)
    except IntegrityError:
        return Response({"detail": "Database integrity error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)