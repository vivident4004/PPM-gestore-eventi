from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db.models.functions import Lower
from django.db.models import Q

from .models import Event, Registration, Category, PriceOption
from .forms import EventForm, AddAttendeeForm, CategoryForm, PriceOptionFormSet, SearchForm

# Event Views
class EventListView(ListView):
    model = Event
    template_name = 'GestoreEventi/event_list.html'
    context_object_name = 'events'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Exclude logically deleted events
        queryset = queryset.filter(is_deleted=False)

        # Exclude adult-only events for non-adult users
        if not self.request.user.is_authenticated or not self.request.user.is_adult():
            queryset = queryset.filter(is_adult_only=False)

        category_slug = self.kwargs.get('category_slug')

        # Filter by category if provided
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(categories=category)

        # Handle search query
        search_query = self.request.GET.get('query', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) | 
                Q(location__icontains=search_query)
            ).distinct()

        # Filter by price
        free_only = self.request.GET.get('free_only')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if free_only:
            # Get events that have no price options or all price options are 0
            queryset = queryset.filter(
                Q(price_options__isnull=True) |
                ~Q(price_options__price__gt=0)
            ).distinct()
        else:
            # Handle price filtering
            try:
                # Case 1: Both min and max price are provided
                if min_price and max_price:
                    min_price = float(min_price)
                    max_price = float(max_price)

                    # Special case: min=0 and max=0 should behave like "show only free events"
                    if min_price == 0 and max_price == 0:
                        queryset = queryset.filter(
                            Q(price_options__isnull=True) |
                            ~Q(price_options__price__gt=0)
                        ).distinct()
                    # Special case: min=0 and max>0 should include both paid events up to max price AND free events
                    elif min_price == 0 and max_price > 0:
                        queryset = queryset.filter(
                            Q(price_options__price__lte=max_price) |
                            Q(price_options__isnull=True) |
                            ~Q(price_options__price__gt=0)
                        ).distinct()
                    else:
                        queryset = queryset.filter(
                            price_options__price__gte=min_price,
                            price_options__price__lte=max_price
                        ).distinct()

                # Case 2: Only min price is provided
                elif min_price:
                    min_price = float(min_price)
                    # Special case: min=0 should include both paid events AND free events
                    if min_price == 0:
                        queryset = queryset.filter(
                            Q(price_options__price__gte=min_price) |
                            Q(price_options__isnull=True) |
                            ~Q(price_options__price__gt=0)
                        ).distinct()
                    else:
                        queryset = queryset.filter(
                            price_options__price__gte=min_price
                        ).distinct()

                # Case 3: Only max price is provided
                elif max_price:
                    max_price = float(max_price)
                    # Include events with price options less than or equal to max_price
                    # OR events that are free (no price options or all price options are 0)
                    queryset = queryset.filter(
                        Q(price_options__price__lte=max_price) |
                        Q(price_options__isnull=True) |
                        ~Q(price_options__price__gt=0)
                    ).distinct()
            except (ValueError, TypeError):
                # If price values are invalid, ignore the filter
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all categories to context for the navigation bar
        context['categories'] = Category.objects.all()

        # Get current category if filtering by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)

        # Add search form to context
        search_query = self.request.GET.get('query', '')
        context['search_form'] = SearchForm(initial={'query': search_query})
        context['search_query'] = search_query

        # Add price filter parameters to context
        context['free_only'] = self.request.GET.get('free_only', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')

        # Ensure all events have their image, end_date, and price properly processed
        for event in context['events']:
            # Ensure image URL is accessible if image exists
            if event.image:
                event.has_image = True
            else:
                event.has_image = False

            # Flag for end_date existence
            event.has_end_date = event.end_date is not None

            # Add price information
            event.price_display = event.get_price_range()
            event.is_free = event.is_free()

        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'GestoreEventi/event_detail.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the event object
        event = self.get_object()

        # Check if the event is for adults only
        if event.is_adult_only:
            # Check if the user is authenticated
            if not request.user.is_authenticated:
                messages.warning(request, _('This event is for adults only. Please log in to continue.'))
                return redirect('login')

            # Check if the user is an adult
            if not request.user.is_adult():
                messages.warning(request, _('This event is for adults only. You must be 18 or older to view it.'))
                return redirect('event-list')

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Get the object from the default implementation
        obj = super().get_object(queryset)
        # Check if the event is deleted
        if obj.is_deleted:
            # If the event is deleted, raise a 404 error
            from django.http import Http404
            raise Http404("Event not found")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_registered'] = Registration.objects.filter(
                event=self.object, 
                attendee=self.request.user
            ).exists()

        # Process image and end_date for the event
        event = context['event']
        if event.image:
            event.has_image = True
        else:
            event.has_image = False

        event.has_end_date = event.end_date is not None

        # Add price information
        event.price_display = event.get_price_range()
        event.is_free = event.is_free()

        # Get all price options for the event
        context['price_options'] = event.price_options.all().order_by('price')

        # Add all categories to context for reference
        context['categories'] = Category.objects.all()

        return context

class OrganizerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Check if user is in Organizers group or is a superuser
        return self.request.user.groups.filter(name='Organizers').exists() or self.request.user.is_superuser

class EventDashboardView(LoginRequiredMixin, OrganizerRequiredMixin, TemplateView):
    template_name = 'GestoreEventi/event_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all events organized by the current user, or all events if superuser
        # Exclude logically deleted events
        if self.request.user.is_superuser:
            context['events'] = Event.objects.filter(is_deleted=False).order_by('-date')
        else:
            context['events'] = Event.objects.filter(organizer=self.request.user, is_deleted=False).order_by('-date')
        return context

class EventCreateView(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = Event
    template_name = 'GestoreEventi/event_form.html'
    form_class = EventForm
    success_url = reverse_lazy('event-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['price_formset'] = PriceOptionFormSet(self.request.POST, instance=self.object or None)
        else:
            context['price_formset'] = PriceOptionFormSet(instance=self.object or None)
        return context

    def form_valid(self, form):
        form.instance.organizer = self.request.user

        # Handle image upload to Vercel Blob if an image is provided
        if 'image' in self.request.FILES:
            from .utils import upload_to_vercel_blob
            try:
                image_url = upload_to_vercel_blob(self.request.FILES['image'])
                form.instance.image = image_url
            except Exception as e:
                messages.error(self.request, _(f'Error uploading image: {str(e)}'))

        self.object = form.save(commit=False)

        price_formset = PriceOptionFormSet(self.request.POST, instance=self.object)
        if not price_formset.is_valid():
            return self.form_invalid(form)

        try:
            self.object.save()
            form.save_m2m()
            price_formset.save()

            new_categories_text = form.cleaned_data.get('new_categories', '')
            if new_categories_text:
                category_names = [name.strip() for name in new_categories_text.split(',') if name.strip()]

                for name in category_names:
                    try:
                        category, created = Category.objects.get_or_create(
                            name__iexact=name,
                            defaults={'name': name, 'slug': slugify(name)}
                        )
                        self.object.categories.add(category)
                    except IntegrityError:
                        messages.warning(self.request, f'Category "{name}" could not be created')

            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f'Error saving event: {str(e)}')
            return self.form_invalid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    template_name = 'GestoreEventi/event_form.html'
    form_class = EventForm

    def get_object(self, queryset=None):
        # Get the object from the default implementation
        obj = super().get_object(queryset)
        # Check if the event is deleted
        if obj.is_deleted:
            # If the event is deleted, raise a 404 error
            from django.http import Http404
            raise Http404("Event not found")
        return obj

    def test_func(self):
        event = self.get_object()
        # Check if user is the organizer of the event or is a superuser
        return self.request.user == event.organizer or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['price_formset'] = PriceOptionFormSet(self.request.POST, instance=self.object)
        else:
            context['price_formset'] = PriceOptionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        # Create the event instance but don't save it to the database yet
        self.object = form.save(commit=False)

        # Process price formset
        price_formset = PriceOptionFormSet(self.request.POST, instance=self.object)
        if not price_formset.is_valid():
            # If the formset is not valid, return to the form with errors
            return self.form_invalid(form)

        # Save the event to the database
        self.object.save()
        form.save_m2m()  # Save many-to-many relationships

        # Save the price formset
        price_formset.save()

        # Process new categories
        new_categories_text = form.cleaned_data.get('new_categories', '')
        if new_categories_text:
            # Split by comma and strip whitespace
            category_names = [name.strip() for name in new_categories_text.split(',') if name.strip()]

            for name in category_names:
                # Check if category already exists (case insensitive)
                if not Category.objects.filter(name__iexact=name).exists():
                    # Create new category
                    category = Category(name=name, slug=slugify(name))
                    category.save()
                    # Add to event's categories
                    self.object.categories.add(category)
                else:
                    # Get existing category and add to event if not already added
                    category = Category.objects.get(name__iexact=name)
                    self.object.categories.add(category)

        # Return a redirect to the success URL
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('event-detail', kwargs={'pk': self.object.pk})

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'GestoreEventi/event_confirm_delete.html'
    success_url = reverse_lazy('event-list')

    def test_func(self):
        event = self.get_object()
        # Check if user is the organizer of the event or is a superuser
        return self.request.user == event.organizer or self.request.user.is_superuser

    def get_object(self, queryset=None):
        # Get the object from the default implementation
        obj = super().get_object(queryset)
        # Check if the event is already deleted
        if obj.is_deleted:
            # If the event is already deleted, raise a 404 error
            from django.http import Http404
            raise Http404("Event not found")
        return obj

    def post(self, request, *args, **kwargs):
        """
        Override the post method to handle the form submission.
        Instead of physically deleting the event, set is_deleted=True.
        """
        self.object = self.get_object()

# Delete the image from Vercel Blob if it exists
if self.object.image and self.object.image.startswith('https://'):
    from .utils import delete_from_vercel_blob
    try:
        delete_from_vercel_blob(self.object.image)
    except Exception as e:
        messages.warning(request, _(f'Error deleting image: {str(e)}'))

        # Logical deletion - set is_deleted flag to True
        self.object.is_deleted = True
        self.object.save()

        messages.success(request, _('Event has been successfully deleted.'))
        return HttpResponseRedirect(self.get_success_url())

# Category Views
class CategoryListView(LoginRequiredMixin, OrganizerRequiredMixin, ListView):
    model = Category
    template_name = 'GestoreEventi/category_list.html'
    context_object_name = 'categories'
    ordering = [Lower('name')]

class CategoryCreateView(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'GestoreEventi/category_form.html'
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        messages.success(self.request, _('category created successfully.'))
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, OrganizerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'GestoreEventi/category_form.html'
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        messages.success(self.request, _('category updated successfully.'))
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, OrganizerRequiredMixin, DeleteView):
    model = Category
    template_name = 'GestoreEventi/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        # Check if the category is used by any events
        if category.events.exists():
            messages.error(request, _('cannot delete category because it is used by one or more events.'))
            return redirect('category-list')
        messages.success(request, _('category deleted successfully.'))
        return super().delete(request, *args, **kwargs)

# Registration Views
@login_required
def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk, is_deleted=False)

    # Check if event is full
    if event.is_full():
        messages.error(request, _('this event is already full.'))
        return redirect('event-detail', pk=pk)

    # Get the selected price option if provided
    price_option = None
    if request.method == 'POST' and 'price_option' in request.POST:
        price_option_id = request.POST.get('price_option')
        try:
            price_option = PriceOption.objects.get(id=price_option_id, event=event)

            # Check if this price option has max_seats and if it's full
            if price_option.max_seats is not None:
                registrations_count = Registration.objects.filter(event=event, price_option=price_option).count()
                if registrations_count >= price_option.max_seats:
                    messages.error(request, _('this price option is already full.'))
                    return redirect('event-detail', pk=pk)
        except PriceOption.DoesNotExist:
            messages.error(request, _('invalid price option selected.'))
            return redirect('event-detail', pk=pk)
    elif event.price_options.count() == 1:
        # If there's only one price option, use it automatically
        price_option = event.price_options.first()

    try:
        Registration.objects.create(event=event, attendee=request.user, price_option=price_option)
        messages.success(request, _('You have successfully registered for') + f' {event.title}.')
    except IntegrityError:
        messages.warning(request, _('You are already registered for this event.'))

    return redirect('event-detail', pk=pk)

@login_required
def unregister_from_event(request, pk):
    event = get_object_or_404(Event, pk=pk, is_deleted=False)

    try:
        registration = Registration.objects.get(event=event, attendee=request.user)
        registration.delete()
        messages.success(request, _('You have successfully unregistered from') + f' {event.title}.')
    except Registration.DoesNotExist:
        messages.warning(request, _('You are not registered for this event.'))

    return redirect('event-detail', pk=pk)

@login_required
def my_registrations(request):
    from django.utils import timezone
    now = timezone.now()

    # Get all registrations for the current user, excluding deleted events
    all_registrations = Registration.objects.filter(attendee=request.user, event__is_deleted=False)

    # Get upcoming events (events that haven't started yet)
    upcoming_registrations = all_registrations.filter(event__date__gt=now).order_by('event__date')

    # Get the next upcoming event(s) - events with the earliest start date
    next_events = []
    if upcoming_registrations.exists():
        next_event_date = upcoming_registrations.first().event.date
        next_events = upcoming_registrations.filter(event__date=next_event_date)

    # Get current events (events that have started but not ended yet)
    current_registrations = all_registrations.filter(
        event__date__lte=now
    ).filter(
        Q(event__end_date__gt=now) | Q(event__end_date__isnull=True)
    ).order_by('event__date')

    # Get past events (events that have ended)
    past_registrations = all_registrations.filter(
        Q(event__end_date__lte=now) | 
        (Q(event__end_date__isnull=True) & Q(event__date__lt=now))
    ).order_by('-event__date')

    # Combine current and upcoming events (excluding next events)
    next_event_ids = [reg.event.id for reg in next_events]
    current_upcoming_registrations = (current_registrations | 
                                     upcoming_registrations.exclude(event__id__in=next_event_ids)
                                    ).order_by('event__date')

    # Check if calendar view is requested
    view_type = request.GET.get('view', 'list')

    context = {
        'next_events': next_events,
        'current_upcoming_registrations': current_upcoming_registrations,
        'past_registrations': past_registrations,
        'view_type': view_type
    }

    return render(request, 'GestoreEventi/my_registrations.html', context)

@login_required
@permission_required('GestoreEventi.view_registration', raise_exception=True)
def event_attendees(request, pk):
    event = get_object_or_404(Event, pk=pk, is_deleted=False)

    # Check if user is the organizer of the event
    if request.user != event.organizer and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to view the attendees of this event.'))
        return redirect('event-detail', pk=pk)

    # Handle adding attendees
    if request.method == 'POST':
        form = AddAttendeeForm(event, request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            price_option = form.cleaned_data.get('price_option')

            # Check if this price option has max_seats and if it's full
            if price_option and price_option.max_seats is not None:
                registrations_count = Registration.objects.filter(event=event, price_option=price_option).count()
                if registrations_count >= price_option.max_seats:
                    messages.error(request, _('this price option is already full.'))
                    return redirect('event-attendees', pk=pk)

            try:
                Registration.objects.create(event=event, attendee=user, price_option=price_option)
                price_info = f" with option '{price_option.name}'" if price_option else ""
                messages.success(request, _(f'User {user.username} has been added to the event{price_info}.'))
            except IntegrityError:
                messages.warning(request, _(f'User {user.username} is already registered for this event.'))
            return redirect('event-attendees', pk=pk)
    else:
        form = AddAttendeeForm(event)

    registrations = Registration.objects.filter(event=event).order_by('registered_at')
    return render(request, 'GestoreEventi/event_attendees.html', {
        'event': event,
        'registrations': registrations,
        'form': form
    })
