from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        blank=True,
        verbose_name=_('Phone number')
    )
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
