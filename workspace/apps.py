from django.apps import AppConfig

class WorkspaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workspace'

    def ready(self):
        import workspace.signals  # Correct relative import
        # Ensure signals are imported when the app is ready
        # This is important to ensure that the signals are registered
        # and will work as expected when the app is running.