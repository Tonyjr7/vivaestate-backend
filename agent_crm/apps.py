from django.apps import AppConfig


class AgentCrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agent_crm"
    def ready(self):
        import agent_crm.signals
