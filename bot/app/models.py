from django.db import models
from django.utils import timezone


class Task(models.Model):
    task_name = models.CharField(max_length=100)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.task_name



class LeaveRequest(models.Model):
    leave_date = models.DateTimeField(default=timezone.now)  # Set default value to current time
    reason = models.TextField()

    def __str__(self):
        return f"Leave on {self.leave_date} for {self.reason}"

