from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    max_attendees = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})

    def is_full(self):
        return self.registration_set.count() >= self.max_attendees

    def available_spots(self):
        return max(0, self.max_attendees - self.registration_set.count())

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'attendee')

    def __str__(self):
        return f"{self.attendee.username} - {self.event.title}"
