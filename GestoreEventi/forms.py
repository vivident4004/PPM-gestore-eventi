# GestoreEventi/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Event, Registration
from django.contrib.auth import get_user_model

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'end_date', 'location', 'max_attendees', 'image']

        # Add labels to ensure proper translation
        labels = {
            'date': _('Date'),
            'end_date': _('End date'),
            'location': _('Location'),
            'max_attendees': _('Max attendees'),
        }

        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5}
            ),
            'location': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'end_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'max_attendees': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1'}
            ),
            'image': forms.FileInput(
                attrs={'class': 'form-control'}
            ),
        }

class AddAttendeeForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('User')
    )

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude users already registered for the event
        registered_users = Registration.objects.filter(event=event).values_list('attendee', flat=True)
        self.fields['user'].queryset = get_user_model().objects.exclude(id__in=registered_users)
