from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ImportantNotification
from .serializers import ImportantNotificationSerializer

@api_view(['GET'])
def important_notifications_list(request):
    """
    Retrieves all stored notifications flagged as important by the AI Agent.
    Ordered by the time they were received, newest first.
    """
    try:
        # Pull down historical flags ordered sequentially by arrival timestamp
        notifications = ImportantNotification.objects.all().order_by('-received_at')
        serializer = ImportantNotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"[API ERROR] Failed to fetch historical notifications: {e}")
        return Response(
            {"error": "Internal server transaction validation error."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
