# GestoreEventi/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Event, Registration, Category, PriceOption
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.forms import inlineformset_factory, modelformset_factory

class EventForm(forms.ModelForm):
    new_categories = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_('Add new categories separated by commas')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sovrascrivi le etichette qui
        self.fields['title'].label = _('title')
        self.fields['description'].label = _('description')
        self.fields['date'].label = _('start date')
        self.fields['end_date'].label = _('end date')
        self.fields['location'].label = _('location')
        self.fields['max_attendees'].label = _('max attendees')
        self.fields['image'].label = _('image')
        self.fields['categories'].label = _('categories')
        self.fields['new_categories'].label = _('new categories')

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'end_date', 'location', 'max_attendees', 'image', 'categories']

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
            'categories': forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        # Check if a category with this name already exists (case insensitive)
        if Category.objects.filter(name__iexact=name).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise forms.ValidationError(_('a category with this name already exists.'))
        return name

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Generate slug from name
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class PriceOptionForm(forms.ModelForm):
    class Meta:
        model = PriceOption
        fields = ['name', 'price', 'max_seats']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'max_seats': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = _('name')
        self.fields['price'].label = _('price')
        self.fields['max_seats'].label = _('max seats')


# Custom formset for PriceOption with validation
class BasePriceOptionFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Check if any forms are marked for deletion
        if any(self.errors):
            return

        # Get the event's max_attendees
        event = self.instance
        max_attendees = event.max_attendees

        # Calculate the sum of max_seats
        total_max_seats = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue

            max_seats = form.cleaned_data.get('max_seats')
            if max_seats:
                total_max_seats += max_seats

        # Validate that the sum doesn't exceed max_attendees
        if total_max_seats > max_attendees:
            raise forms.ValidationError(
                _("The sum of max seats (%(total)s) exceeds the event's maximum attendees (%(max)s)."),
                params={'total': total_max_seats, 'max': max_attendees},
            )

# Create a formset for PriceOption
PriceOptionFormSet = inlineformset_factory(
    Event, 
    PriceOption, 
    form=PriceOptionForm,
    formset=BasePriceOptionFormSet,
    extra=1,  # Start with one empty form
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class PriceOptionSelectionForm(forms.Form):
    price_option = forms.ModelChoiceField(
        queryset=PriceOption.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('price option')
    )

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show price options for this event
        self.fields['price_option'].queryset = event.price_options.all().order_by('price')

        # If there's only one price option, select it by default
        if event.price_options.count() == 1:
            self.fields['price_option'].initial = event.price_options.first()


class AddAttendeeForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('user')
    )

    price_option = forms.ModelChoiceField(
        queryset=PriceOption.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('price option'),
        required=False
    )

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude users already registered for the event
        registered_users = Registration.objects.filter(event=event).values_list('attendee', flat=True)
        self.fields['user'].queryset = get_user_model().objects.exclude(id__in=registered_users)

        # Only show price options for this event
        self.fields['price_option'].queryset = event.price_options.all().order_by('price')

        # If there's only one price option, select it by default
        if event.price_options.count() == 1:
            self.fields['price_option'].initial = event.price_options.first()
