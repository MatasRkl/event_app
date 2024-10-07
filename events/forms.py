from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Event, Booking, Review


class EmailUpdateForm(forms.ModelForm):
    """
        A form to update the email address of the user.

        Inherits from forms.ModelForm and links to the User model. It updates the email field with a form control class and
        adds a placeholder to the input. This form requires the email field to be filled in.

        Meta:
            model (User): The model used for the form (User model).
            fields (list): The fields from the model to be included in the form (only 'email').

        Methods:
            __init__(self, *args, **kwargs): Customizes the email field, making it required and adding widget attributes
            (CSS class and placeholder).
    """
    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })


class CustomUserCreationForm(UserCreationForm):
    """
        A custom user creation form that extends Django's UserCreationForm.

        This form includes additional fields for first name, last name, and email, in addition to the default password fields.
        It overrides the save method to create a username based on the user's first and last name.

        Meta:
            model (User): The model used for the form (User model).
            fields (tuple): The fields included in the form (first_name, last_name, email, password1, password2).

        Methods:
            save(self, commit=True): Saves the form, generating a username based on the user's first and last name,
            and saves the user if commit is True.
    """
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = f"{user.first_name.lower()}.{user.last_name.lower()}"
        if commit:
            user.save()
        return user


class EventForm(forms.ModelForm):
    """
        A form for creating and editing events.

        This form includes fields for title, description, date, venue, city, latitude, longitude, category, image, and
        ticket price. It is linked to the Event model.

        Meta:
            model (Event): The model used for the form (Event model).
            fields (list): The fields included in the form (title, description, date, venue, city, latitude, longitude,
            category, image, ticket_price).
    """
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'venue', 'city', 'latitude', 'longitude', 'category', 'image',
                  'ticket_price']


class BookingForm(forms.ModelForm):
    """
        A form for making event bookings.

        Meta:
            model (Booking): The model used for the form (Booking model).
            fields (list): The fields included in the form.
    """
    class Meta:
        model = Booking
        fields = []


class ReviewForm(forms.ModelForm):
    """
        A form for submitting event reviews.

        This form includes fields for the review rating and comment. The rating field uses a RadioSelect widget with
        choices from 1 to 5 stars.

        Meta:
            model (Review): The model used for the form (Review model).
            fields (list): The fields included in the form (rating and comment).
            widgets (dict): Custom widget for the rating field using RadioSelect with choices from 1 to 5 stars.
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
        }
