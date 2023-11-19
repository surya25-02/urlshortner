from django.apps import AppConfig

class ShortnerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shortner'
 
    def ready(self):
        from .updater import scheduler
        scheduler.start()