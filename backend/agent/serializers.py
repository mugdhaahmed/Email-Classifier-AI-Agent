from rest_framework import serializers
from .models import ImportantNotification

class ImportantNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportantNotification
        fields = [
            'id', 
            'email_id', 
            'sender', 
            'subject', 
            'priority', 
            'category', 
            'reason', 
            'received_at'
        ]