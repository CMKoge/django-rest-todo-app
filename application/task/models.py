from django.db import models

# Create your models here.
# tasks/models.py
from django.db import models

class Task(models.Model):
    class State(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"
        CANCELLED = "CANCELLED", "Cancelled"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True) # URL or path to image
    state = models.CharField(
        max_length=32,
        choices=State.choices,
        default=State.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)   # last updated

    def __str__(self):
        return f"{self.id} - {self.title} ({self.state})"
