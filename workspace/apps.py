from django.apps import AppConfig

def ready(self):
    import .signals


class WorkspaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workspace'
