from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from .models import Event, Registration
from .forms import EventForm, AddAttendeeForm

# Event Views
class EventListView(ListView):
    model = Event
    template_name = 'GestoreEventi/event_list.html'
    context_object_name = 'events'
    ordering = ['-date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure all events have their image and end_date properly processed
        for event in context['events']:
            # Ensure image URL is accessible if image exists
            if event.image:
                event.has_image = True
            else:
                event.has_image = False

            # Flag for end_date existence
            event.has_end_date = event.end_date is not None

        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'GestoreEventi/event_detail.html'

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
        if self.request.user.is_superuser:
            context['events'] = Event.objects.all().order_by('-date')
        else:
            context['events'] = Event.objects.filter(organizer=self.request.user).order_by('-date')
        return context

class EventCreateView(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = Event
    template_name = 'GestoreEventi/event_form.html'
    form_class = EventForm
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    template_name = 'GestoreEventi/event_form.html'
    form_class = EventForm

    def test_func(self):
        event = self.get_object()
        # Check if user is the organizer of the event or is a superuser
        return self.request.user == event.organizer or self.request.user.is_superuser

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

# Registration Views
@login_required
def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Check if event is full
    if event.is_full():
        messages.error(request, _('This event is already full.'))
        return redirect('event-detail', pk=pk)

    try:
        Registration.objects.create(event=event, attendee=request.user)
        messages.success(request, _('You have successfully registered for') + f' {event.title}.')
    except IntegrityError:
        messages.warning(request, _('You are already registered for this event.'))

    return redirect('event-detail', pk=pk)

@login_required
def unregister_from_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    try:
        registration = Registration.objects.get(event=event, attendee=request.user)
        registration.delete()
        messages.success(request, _('You have successfully unregistered from') + f' {event.title}.')
    except Registration.DoesNotExist:
        messages.warning(request, _('You are not registered for this event.'))

    return redirect('event-detail', pk=pk)

@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(attendee=request.user).order_by('-event__date')
    return render(request, 'GestoreEventi/my_registrations.html', {'registrations': registrations})

@login_required
@permission_required('GestoreEventi.view_registration', raise_exception=True)
def event_attendees(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Check if user is the organizer of the event
    if request.user != event.organizer and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to view the attendees of this event.'))
        return redirect('event-detail', pk=pk)

    # Handle adding attendees
    if request.method == 'POST':
        form = AddAttendeeForm(event, request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            try:
                Registration.objects.create(event=event, attendee=user)
                messages.success(request, _(f'User {user.username} has been added to the event.'))
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
