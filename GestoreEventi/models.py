from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(verbose_name='Date')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='End date')
    location = models.CharField(max_length=200, verbose_name='Location')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    max_attendees = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})

    def is_full(self):
        return self.registration_set.count() >= self.max_attendees

    def available_spots(self):
        return max(0, self.max_attendees - self.registration_set.count())

    def formatted_date(self):
        """Return the date formatted in European style with 24-hour time."""
        from django.utils.formats import date_format
        return date_format(self.date, format='d/m/Y H:i', use_l10n=False)

    def formatted_end_date(self):
        """Return the end date formatted in European style with 24-hour time, if it exists."""
        if not self.end_date:
            return None
        from django.utils.formats import date_format
        return date_format(self.end_date, format='d/m/Y H:i', use_l10n=False)

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'attendee')

    def __str__(self):
        return f"{self.attendee.username} - {self.event.title}"

    def formatted_registered_at(self):
        """Return the registration date formatted in European style with 24-hour time."""
        from django.utils.formats import date_format
        return date_format(self.registered_at, format='d/m/Y H:i', use_l10n=False)
