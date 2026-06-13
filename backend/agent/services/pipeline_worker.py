import time
import threading
from django.utils.dateparse import parse_datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from agent.models import ProcessedEmail, ImportantNotification
from agent.services.ai_classifier import AIClassifierService
from agent.services.sources import get_email_source

def start_email_pipeline():
    """Wrapper initializer to safely spin up the background worker thread."""
    worker_thread = threading.Thread(target=_run_pipeline_loop, daemon=True)
    worker_thread.start()

def _run_pipeline_loop():
    """Continuous automated polling loop handler executing every 2 minutes."""
    print("[PIPELINE WORKER STARTED] Background processing routine active.")
    
    # Instantiate our error-free LangChain service
    ai_service = AIClassifierService()
    channel_layer = get_channel_layer()

    # Select the active ingestion source (mock JSON or real Gmail) via MOCK_MODE.
    # Built once so the Gmail service client / token are reused across cycles.
    source = get_email_source()
    print(f"[PIPELINE SOURCE] Using ingestion source: {type(source).__name__}")

    while True:
        try:
            # Pull this cycle's batch from whichever source is active.
            emails = source.fetch()

            for mail in emails:
                email_id = mail.get('email_id')

                # GUARDRAIL: Strict duplicate identification check
                if ProcessedEmail.objects.filter(email_id=email_id).exists():
                    # Silently skip processed assets [cite: 6, 15]
                    continue

                print(f"[PROCESSING NEW EMAIL] ID: {email_id} | Subject: {mail.get('subject')}")

                # Analyze email structure via LangChain node [cite: 9]
                analysis = ai_service.analyze_email(
                    sender=mail.get('sender', ''),
                    subject=mail.get('subject', ''),
                    body=mail.get('body', '')
                )

                # Track that we have checked this element to prevent infinite loops
                ProcessedEmail.objects.create(email_id=email_id)

                # If classified as important, store and broadcast it [cite: 11]
                if analysis.important:
                    received_at_dt = parse_datetime(mail.get('received_at', '') or '')

                    # Persist structured notice to database logs
                    notification = ImportantNotification.objects.create(
                        email_id=email_id,
                        sender=mail.get('sender', ''),
                        subject=mail.get('subject', ''),
                        priority=analysis.priority,
                        category=analysis.category,
                        reason=analysis.reason,
                        received_at=received_at_dt
                    )

                    # Generate payload dictionary
                    payload = {
                        "id": notification.pk,  # Swapped from .id to .pk to satisfy type checkers
                        "email_id": notification.email_id,
                        "sender": notification.sender,
                        "subject": notification.subject,
                        "priority": notification.priority,
                        "category": notification.category,
                        "reason": notification.reason,
                        "received_at": mail.get('received_at', '')
                    }

                    # Stream the payload directly to the frontend WebSocket channel
                    if channel_layer is not None:
                        async_to_sync(channel_layer.group_send)(
                            "email_notifications",
                            {
                                "type": "send_notification",
                                "data": payload
                            }
                        )
                        print(f"[PIPELINE BROADCAST SUCCESS] Alert sent out via socket group layer.")

        except Exception as e:
            print(f"[CRITICAL LOOP SYSTEM ERROR] Exception thrown during loop cycle: {e}")

        # Set sleep interval to 2 minutes as required by the specifications
        time.sleep(120)