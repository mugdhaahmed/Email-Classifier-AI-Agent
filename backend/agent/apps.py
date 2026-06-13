import os
import sys
from django.apps import AppConfig


class AgentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent'

    def ready(self):
        """
        Lifecycle hook executed on server boot. Spins up the background polling
        thread, but ONLY when actually serving requests:

        - `manage.py runserver` -> start, but only in the autoreloader's child
          process (RUN_MAIN='true') to avoid a double start.
        - daphne / gunicorn      -> not launched through manage.py, so argv[0]
          does not end with 'manage.py'; start directly.
        - any other manage.py command (migrate, check, gmail_auth, shell, ...)
          -> do NOT start the worker.
        """
        from decouple import config

        # Allow disabling the worker entirely via env (e.g. during tests).
        if not config('PIPELINE_AUTOSTART', default=True, cast=bool):
            return

        argv = sys.argv
        run_via_manage = bool(argv) and os.path.basename(argv[0]) == 'manage.py'

        if run_via_manage:
            is_runserver = len(argv) > 1 and argv[1] == 'runserver'
            if not is_runserver:
                return
            # runserver's reloader runs ready() twice; only start in the child.
            if os.environ.get('RUN_MAIN') != 'true':
                return

        from agent.services import pipeline_worker
        pipeline_worker.start_email_pipeline()
