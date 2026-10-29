from django.conf import settings
from django.db import models


class Note(models.Model):
    title = models.CharField(max_length=120)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["id"]
