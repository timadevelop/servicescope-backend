from django.db import models

from authentication.models import User
# Create your models here.

class Feedback(models.Model):
    """
    Service feedback from user
    """
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='feedbacks')
    text = models.TextField(max_length=2000, blank=True)
    rate = models.DecimalField(max_digits=2, decimal_places=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
