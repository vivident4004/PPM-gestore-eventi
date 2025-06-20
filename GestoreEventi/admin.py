from django.contrib import admin
from .models import Event, Registration

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'organizer', 'max_attendees', 'available_spots', 'is_full')
    list_filter = ('date', 'location')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'

    def available_spots(self, obj):
        return obj.available_spots()

    def is_full(self, obj):
        return obj.is_full()

    is_full.boolean = True

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'attendee', 'registered_at')
    list_filter = ('registered_at', 'event')
    search_fields = ('event__title', 'attendee__username', 'attendee__email')
    date_hierarchy = 'registered_at'
