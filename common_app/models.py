from django.db import models

# Create your models here.

class BaseModel(models.Model):
    """Abstract Model with basic datetime fields for forensics."""

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
