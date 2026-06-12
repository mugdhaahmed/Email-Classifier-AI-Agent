from django.db import models


class ProcessedEmail(models.Model):
    """
    Tracks every email ID pulled by the engine. 
    Guarantees absolute duplicate prevention at the database level.
    """
    email_id = models.CharField(max_length=255, unique=True, db_index=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Processed ID: {self.email_id}"


class ImportantNotification(models.Model):
    """
    Stores structured notifications flagged as important by the AI Agent.
    """
    PRIORITY_CHOICES = [
        ('HIGH', 'HIGH'),
        ('MEDIUM', 'MEDIUM'),
        ('LOW', 'LOW'),
    ]

    email_id = models.CharField(max_length=255, unique=True)
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    category = models.CharField(max_length=100)
    reason = models.TextField()
    received_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.priority}][{self.category}] - {self.subject}"