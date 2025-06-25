from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import Group
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import CustomUser
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm Password'), widget=forms.PasswordInput)
    is_organizer = forms.BooleanField(label=_('Register as Event Organizer'), required=False)
    date_of_birth = forms.DateField(
        label=_('Date of Birth'), 
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text=_('Required to access adult-only events')
    )
    address = forms.CharField(
        label=_('Address'),
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_('Used for billing purposes only')
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'phone', 'bio', 'date_of_birth', 'address')

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


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth', 'address', 'phone', 'bio']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(
                format='%Y-%m-%d', # Formato standard che HTML5 capisce
                attrs ={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'pattern': '\\+?\\d{9,15}',
                'title': _('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
            }),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        help_texts = {
            'date_of_birth': _('Required to access adult-only events'),
            'address': _('Used for billing purposes only'),
        }


class UserProfileView(LoginRequiredMixin, UpdateView):
    """View for updating user profile information."""

    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('user-profile')

    def get_object(self, queryset=None):
        """Return the current user's profile."""
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'password_form' not in context:
            context['password_form'] = SetPasswordForm(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Distinguiamo quale form è stato inviato
        if 'change_password' in request.POST:
            password_form = SetPasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantiene l'utente loggato
                messages.success(request, _('Your password has been changed successfully.'))
                return redirect(self.get_success_url())
            else:
                # Se il form non è valido, renderizza di nuovo la pagina con gli errori
                context = self.get_context_data(password_form=password_form)
                return self.render_to_response(context)
        else:
            # Altrimenti, gestisci il form del profilo
            return super().post(request, *args, **kwargs)


    def form_valid(self, form):
        """Handle valid form submission."""
        messages.success(self.request, _('Your profile has been updated successfully.'))
        return super().form_valid(form)
