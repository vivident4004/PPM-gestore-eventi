from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import CustomUser
from django import forms
from django.utils.translation import gettext_lazy as _

class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm Password'), widget=forms.PasswordInput)
    is_organizer = forms.BooleanField(label=_('Register as Event Organizer'), required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'phone', 'bio')

    # def clean_password2(self):
    #     password1 = self.cleaned_data.get('password1')
    #     password2 = self.cleaned_data.get('password2')
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError(_('Passwords do not match'))
    #     return password2

class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()

        # Add user to appropriate group
        if form.cleaned_data['is_organizer']:
            group = Group.objects.get(name='Organizers')
        else:
            group = Group.objects.get(name='Attendees')

        user.groups.add(group)

        # Log the user in
        login(self.request, user)
        messages.success(self.request, _('Account created successfully! You are now logged in as') + f' {user.username}.')

        return redirect(self.success_url)

def custom_logout(request):
    """
    Custom logout view that ensures the session is properly terminated
    and redirects to the main page.
    """
    logout(request)
    messages.success(request, _('You have been successfully logged out.'))
    return redirect('event-list')
