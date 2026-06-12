import os
from django.apps import AppConfig

class AgentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent'

    def ready(self):
        """
        Lifecycle hook executed immediately upon server instance boot.
        Spins up the asynchronous background thread process.
        """
        # Ensure thread does not double-trigger during hot-reloads under local development
        if os.environ.get('RUN_MAIN') == 'true':
            from agent.services import pipeline_worker
            pipeline_worker.start_email_pipeline()