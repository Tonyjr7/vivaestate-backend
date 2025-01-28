from django.db import models
from accounts.models import User, Audit
from django.conf import settings
from client_app.models import Property
from app.models import Client

class Favourite(Audit):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'property')  # Ensure a user can only like a property once

class Follow(Audit):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(Client, on_delete=models.CASCADE)