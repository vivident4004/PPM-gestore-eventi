from django.db import models
from django.db.models.functions import Lower
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.formats import number_format

# Create your models here.
def format_price(price):
    """Format a price with the Euro symbol using the current locale's decimal separator."""
    if price is None:
        return ""
    return f"{number_format(price, decimal_pos=2)} €"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = [Lower('name')]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event-list-by-category', kwargs={'category_slug': self.slug})

class PriceOption(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    max_seats = models.IntegerField(null=True, blank=True, verbose_name=_('max seats'))
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='price_options')

    def __str__(self):
        return f"{self.name}: {format_price(self.price)}"

    def is_free(self):
        return self.price == 0

    def available_spots(self):
        """Return the number of available spots for this price option."""
        if self.max_seats is None:
            return self.event.available_spots()
        registrations_count = self.registrations.count()
        return max(0, self.max_seats - registrations_count)

    def is_full(self):
        """Return True if this price option is full."""
        if self.max_seats is None:
            return self.event.is_full()
        return self.registrations.count() >= self.max_seats

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
    categories = models.ManyToManyField(Category, related_name='events', blank=True)

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

    def is_free(self):
        """Return True if all price options are 0 or there are no price options."""
        if not self.price_options.exists():
            return True  # If there are no price options, consider it free
        return all(option.is_free() for option in self.price_options.all())

    def get_min_price(self):
        """Return the minimum price of all price options, or None if the event is free."""
        # Check if is_free is a boolean or a callable method
        if isinstance(self.is_free, bool):
            is_free_value = self.is_free
        else:
            is_free_value = self.is_free()

        if is_free_value:
            return None
        if not self.price_options.exists():
            return None
        return min(option.price for option in self.price_options.all())

    def get_max_price(self):
        """Return the maximum price of all price options, or None if the event is free."""
        # Check if is_free is a boolean or a callable method
        if isinstance(self.is_free, bool):
            is_free_value = self.is_free
        else:
            is_free_value = self.is_free()

        if is_free_value:
            return None
        if not self.price_options.exists():
            return None
        return max(option.price for option in self.price_options.all())

    def get_min_price_with_currency(self):
        """Return the minimum price with currency symbol, or 'Free' if the event is free."""
        # Check if is_free is a boolean or a callable method
        if isinstance(self.is_free, bool):
            is_free_value = self.is_free
        else:
            is_free_value = self.is_free()

        if is_free_value:
            return _("Free")
        min_price = self.get_min_price()
        if min_price is None:
            return ""
        return format_price(min_price)

    def get_price_range(self):
        """Return a string with the price range (from min to max) or just the price if there's only one option."""
        # Check if there are any price options
        if not self.price_options.exists():
            return _("Free")  # If no price options, display as free

        # Check if is_free is a boolean or a callable method
        if isinstance(self.is_free, bool):
            is_free_value = self.is_free
        else:
            is_free_value = self.is_free()

        if is_free_value:
            return _("Free")

        # Get all non-empty price options (price > 0)
        non_free_options = self.price_options.filter(price__gt=0)

        # If there are no non-free options, return "Free"
        if not non_free_options.exists():
            return _("Free")

        # Calculate min and max prices from non-free options
        min_price = min(option.price for option in non_free_options)
        max_price = max(option.price for option in non_free_options)

        if min_price == max_price:
            return format_price(min_price)
        else:
            return _("from %(min_price)s € to %(max_price)s €") % {'min_price': number_format(min_price, decimal_pos=2), 'max_price': number_format(max_price, decimal_pos=2)}

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    price_option = models.ForeignKey(PriceOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'attendee')

    def __str__(self):
        price_info = f" ({self.price_option.name})" if self.price_option else ""
        return f"{self.attendee.username} - {self.event.title}{price_info}"

    def formatted_registered_at(self):
        """Return the registration date formatted in European style with 24-hour time."""
        from django.utils.formats import date_format
        return date_format(self.registered_at, format='d/m/Y H:i', use_l10n=False)
