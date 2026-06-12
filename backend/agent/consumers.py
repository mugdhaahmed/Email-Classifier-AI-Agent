import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Invoked when a frontend dashboard client initiates a handshake connection."""
        self.group_name = "email_notifications"

        # Join the shared notification group layer cleanly
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the handshake persistence pipe
        await self.accept()
        print(f"[WEBSOCKET CONNECTED] Client registered to group: {self.group_name}")

    async def disconnect(self, code):
        """Invoked when a user closes or refreshes the dashboard interface."""
        # Clean up group layer footprint upon exit
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"[WEBSOCKET DISCONNECTED] Client left group: {self.group_name} with code: {code}")

    async def send_notification(self, event):
        """
        Custom event handler method invoked by our background thread worker nodes.
        Pushes a clean structured data packet out across the established socket.
        """
        notification_data = event["data"]
        
        # Send text frames down directly to the active React states
        await self.send(text_data=json.dumps(notification_data))