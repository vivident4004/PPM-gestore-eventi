from django.contrib import admin
from .models import Event, Registration, Category

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'organizer', 'max_attendees', 'available_spots', 'is_full', 'is_deleted')
    list_filter = ('date', 'location', 'categories', 'is_deleted')
    search_fields = ('title', 'description', 'location')
    filter_horizontal = ('categories',)
    date_hierarchy = 'date'
    actions = ['restore_events']

    def get_queryset(self, request):
        # By default, show only non-deleted events
        queryset = super().get_queryset(request)
        # If we're not on the changelist page, return all events
        if request.path != request.path_info:
            return queryset
        # If is_deleted is explicitly set in the filter, respect that
        if 'is_deleted' in request.GET:
            return queryset
        # Otherwise, show only non-deleted events
        return queryset.filter(is_deleted=False)

    def restore_events(self, request, queryset):
        """Action to restore logically deleted events."""
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f"{updated} events have been successfully restored.")
    restore_events.short_description = "Restore selected events"

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
