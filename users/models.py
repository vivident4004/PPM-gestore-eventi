from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(verbose_name=_('Date of Birth'), null=True, blank=True)
    address = models.TextField(verbose_name=_('Address'), blank=True, help_text=_('Used for billing purposes only'))

    def is_adult(self):
        """Check if the user is an adult (18 years or older)"""
        if not self.date_of_birth:
            return False
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age >= 18
