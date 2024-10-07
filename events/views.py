from datetime import datetime

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import EmailUpdateForm, CustomUserCreationForm, EventForm, ReviewForm
from .models import Event, Booking, Category, Review, SavedEvent


@login_required
def homepage(request):
    """
        Displays the homepage with popular and recommended events.

        The popular events are determined based on the number of bookings.
        Recommended events are based on categories of events the user has previously booked.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The rendered homepage with popular and recommended events.
    """
    popular_events = Event.objects.annotate(num_bookings=Count('booking')).order_by('-num_bookings')[:5]

    user_booked_categories = Booking.objects.filter(user=request.user).values_list('event__category', flat=True)
    if user_booked_categories.exists():
        recommended_events = (
            Event.objects.filter(category__in=user_booked_categories).exclude(booking__user=request.user).distinct())[:5]
    else:
        recommended_events = Event.objects.all().order_by('-date')[:5]

    context = {
        'popular_events': popular_events,
        'recommended_events': recommended_events,
    }

    return render(request, 'events/homepage.html', context)


def get_filtered_events(query=None, category_filter=None):
    """
    Utility function to filter events based on a query and category filter.

    Args:
        query (str): The search query to filter event titles.
        category_filter (int): The category ID to filter events by.

    Returns:
        QuerySet: A queryset of filtered events.
    """
    events = Event.objects.all()
    if query:
        events = events.filter(Q(title__icontains=query))
    if category_filter:
        events = events.filter(category=category_filter)
    return events


def event_list(request):
    """
        Displays a list of events with filtering options for category, date, location, and price.

        Args:
            request: The HTTP request object containing GET parameters for filtering.

        Returns:
            HttpResponse: The rendered event list with filtering options.
    """
    events = Event.objects.all()
    categories = Category.objects.all()

    selected_category = request.GET.get('category')
    if selected_category:
        try:
            selected_category = int(selected_category)
            events = events.filter(category__id=selected_category)
        except ValueError:
            selected_category = None

    query = request.GET.get('q')
    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))

    date_filter = request.GET.get('date')
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, "%Y-%m-%d")
            events = events.filter(date__date=date_obj)
        except ValueError:
            pass

    location_filter = request.GET.get('location')
    if location_filter:
        events = events.filter(venue__icontains=location_filter)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        events = events.filter(ticket_price__gte=min_price)
    if max_price:
        events = events.filter(ticket_price__lte=max_price)

    context = {
        'events': events,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'date_filter': date_filter,
        'location_filter': location_filter,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, 'events/event_list.html', context)


def register(request):
    """
        Handles user registration. If the form is valid, the user is registered and logged in.

        Args:
            request: The HTTP request object containing POST data for registration.

        Returns:
            HttpResponse: The rendered registration form or a redirect to the profile page on success.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'You have successfully registered!')
            return redirect('profile')
        else:
            messages.error(request, 'There was an error with your registration.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'events/register.html', {'form': form})


@login_required
def profile(request):
    """
        Displays the user's profile with the option to update their email.
        Also displays events created by the user and events they have booked.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The rendered profile page.
    """
    if request.method == 'POST':
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your email address has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'There was an error updating your email.')
    else:
        form = EmailUpdateForm(instance=request.user)

    created_events = Event.objects.filter(organizer=request.user).annotate(num_bookings=Count('booking'))

    bookings = Booking.objects.filter(user=request.user).select_related('event')
    booked_events = [booking.event for booking in bookings]

    context = {
        'form': form,
        'username': request.user.username,
        'email': request.user.email,
        'created_events': created_events,
        'booked_events': booked_events,
    }

    return render(request, 'events/profile.html', context)


@login_required
def update_email(request):
    """
        Allows the user to update their email address.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The rendered email update form or a redirect to the profile page on success.
    """
    if request.method == 'POST':
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your email address has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating your email address.')
    else:
        form = EmailUpdateForm(instance=request.user)

    return render(request, 'events/update_email.html', {'form': form})


@login_required
def event_detail(request, id):
    """
        Displays the details of a specific event, including reviews and the option to leave a review.

        Users who have booked the event can leave a review. Users can also save or unsave the event.

        Args:
            request: The HTTP request object.
            id (int): The ID of the event.

        Returns:
            HttpResponse: The rendered event detail page.
    """
    event = get_object_or_404(Event, id=id)
    reviews = event.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    user_has_booked = Booking.objects.filter(user=request.user, event=event).exists()

    user_saved_event = SavedEvent.objects.filter(user=request.user, event=event).exists()

    existing_review = Review.objects.filter(user=request.user, event=event).first()

    if request.method == 'POST' and user_has_booked:
        if existing_review:
            messages.error(request, 'You have already submitted a review for this event.')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                try:
                    review = form.save(commit=False)
                    review.event = event
                    review.user = request.user
                    review.save()
                    messages.success(request, 'Your review has been submitted.')
                except IntegrityError:
                    messages.error(request, 'A review from you already exists for this event.')
            else:
                messages.error(request, 'There was an error with your review submission.')
        return redirect('event_detail', id=event.id)

    else:
        form = ReviewForm()

    context = {
        'event': event,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_has_booked': user_has_booked,
        'user_saved_event': user_saved_event,
        'form': form,
        'existing_review': existing_review,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def create_event(request):
    """
        Allows users to create a new event.

        The logged-in user is automatically assigned as the event organizer.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The rendered event creation form or a redirect to the event detail page on success.
    """
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', id=event.id)
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})


@login_required
def book_ticket(request, event_id):
    """
        Allows a user to book a ticket for an event.

        The user can only book one ticket per event.

        Args:
            request: The HTTP request object.
            event_id (int): The ID of the event to book.

        Returns:
            HttpResponse: A redirect to the event detail page or the ticket booking page.
    """
    event = get_object_or_404(Event, id=event_id)

    if Booking.objects.filter(user=request.user, event=event).exists():
        messages.error(request, 'You have already booked a ticket for this event.')
        return redirect('event_detail', id=event_id)

    if request.method == 'POST':
        Booking.objects.create(user=request.user, event=event)
        messages.success(request, 'Ticket booked successfully!')
        return redirect('event_detail', id=event_id)

    return render(request, 'events/book_ticket.html', {'event': event})


@login_required
def dashboard(request):
    """
        Displays the user's dashboard with events they've created and events they've booked.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The rendered dashboard.
    """
    created_events = Event.objects.filter(organizer=request.user)

    bookings = Booking.objects.filter(user=request.user).select_related('event')
    booked_events = [booking.event for booking in bookings]

    context = {
        'created_events': created_events,
        'booked_events': booked_events,
    }

    return render(request, 'events/dashboard.html', context)


@login_required
def edit_event(request, id):
    """
        Allows the organizer to edit an event.

        Only the event organizer can edit the event.

        Args:
            request: The HTTP request object.
            id (int): The ID of the event to edit.

        Returns:
            HttpResponse: The rendered event edit form or a redirect to the event detail page on success.
    """
    event = get_object_or_404(Event, id=id)

    if event.organizer != request.user:
        messages.error(request, 'You are not authorized to edit this event.')
        return redirect('event_detail', id=event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, id):
    """
        Allows the organizer to delete an event.

        Only the event organizer can delete the event.

        Args:
            request: The HTTP request object.
            id (int): The ID of the event to delete.

        Returns:
            HttpResponse: A redirect to the dashboard on successful deletion or the event detail page on error.
    """
    event = get_object_or_404(Event, id=id)

    if event.organizer != request.user:
        messages.error(request, 'You are not authorized to delete this event.')
        return redirect('event_detail', id=event.id)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('dashboard')

    return render(request, 'events/delete_event.html', {'event': event})


@login_required
def event_analytics(request, event_id):
    """
        Displays analytics for a specific event, including bookings and attendee information.

        Only the event organizer can view the analytics.

        Args:
            request: The HTTP request object.
            event_id (int): The ID of the event to view analytics for.

        Returns:
            HttpResponse: The rendered event analytics page.
    """
    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user:
        raise PermissionDenied

    bookings = Booking.objects.filter(event=event)
    attendees = [booking.user for booking in bookings]

    context = {
        'event': event,
        'bookings': bookings,
        'attendees': attendees,
    }

    return render(request, 'events/event_analytics.html', context)


def event_calendar_data(request):
    """
        Provides event data in JSON format for FullCalendar to display on the calendar view.

        Retrieves all events from the database, formats them into a list of dictionaries containing the event title,
        start date in ISO 8601 format, and URL linking to the event detail page. The data is returned as a JSON response

        Args:
            request: The HTTP request object.

        Returns:
            JsonResponse: A list of events in JSON format, including title, start date, and URL for FullCalendar.
    """
    events = Event.objects.all()
    event_list = []
    for event in events:
        event_list.append({
            'title': event.title,
            'start': event.date.isoformat(),
            'url': f"/events/{event.id}/",
        })
    return JsonResponse(event_list, safe=False)


def event_calendar_view(request):
    """
        Renders the event calendar view.

        This view displays a page with a calendar that pulls data from the `event_calendar_data` endpoint.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The rendered calendar template.
    """
    return render(request, 'events/event_calendar.html')


@login_required
def save_event(request, event_id):
    """
        Allows a user to save an event to their saved events list.

        If the event is already saved, an informational message is displayed. Otherwise, the event is saved,
        and a success message is shown.

        Args:
            request: The HTTP request object.
            event_id (int): The ID of the event to save.

        Returns:
            HttpResponse: Redirects to the event detail page, with a success or informational message.
    """
    event = get_object_or_404(Event, id=event_id)
    saved_event, created = SavedEvent.objects.get_or_create(user=request.user, event=event)

    if created:
        messages.success(request, 'Event saved successfully!')
    else:
        messages.info(request, 'You have already saved this event.')

    return redirect('event_detail', id=event.id)


@login_required
def unsave_event(request, event_id):
    """
        Allows a user to remove an event from their saved events list.

        If the event is not saved, an informational message is displayed. Otherwise, the event is removed from the saved
        list, and a success message is shown.

        Args:
            request: The HTTP request object.
            event_id (int): The ID of the event to unsave.

        Returns:
            HttpResponse: Redirects to the event detail page, with a success or informational message.
    """
    event = get_object_or_404(Event, id=event_id)
    saved_event = SavedEvent.objects.filter(user=request.user, event=event).first()

    if saved_event:
        saved_event.delete()
        messages.success(request, 'Event unsaved successfully!')
    else:
        messages.info(request, 'This event was not saved.')

    return redirect('event_detail', id=event.id)


@login_required
def saved_events(request):
    """
        Displays a list of events that the user has saved.

        This view retrieves all events saved by the user and renders them on a page.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The rendered template displaying the user's saved events.
    """
    saved_events = SavedEvent.objects.filter(user=request.user).select_related('event')

    context = {
        'saved_events': saved_events,
    }

    return render(request, 'events/saved_events.html', context)


def skiddle_popular_events(request):
    """
        Fetches and displays the most popular events from the Skiddle API.

        Events are fetched based on their popularity and paginated with 10 events per page.
        The data is retrieved from the Skiddle API and displayed in a paginated format.

        Args:
            request: The HTTP request object, containing pagination parameters (GET method).

        Returns:
            HttpResponse: The rendered template displaying the paginated list of popular events.
    """
    api_key = settings.SKIDDLE_API_KEY
    page = request.GET.get('page', 1)
    items_per_page = 10

    response = (requests.get(f"https://www.skiddle.com/api/v1/events/?api_key={api_key}&limit={items_per_page}&order=popularity"))
    data = response.json()

    events = data.get('results', [])
    paginator = Paginator(events, items_per_page)
    paginated_events = paginator.get_page(page)

    context = {
        'events': paginated_events,
    }
    return render(request, 'events/skiddle_popular_events.html', context)


def skiddle_festivals(request):
    """
        Fetches and displays festival events from the Skiddle API.

        The events are filtered by the festival event code (FEST) and paginated with 10 events per page.
        The data is retrieved from the Skiddle API and displayed in a paginated format.

        Args:
            request: The HTTP request object, containing pagination parameters (GET method).

        Returns:
            HttpResponse: The rendered template displaying the paginated list of festival events.
    """
    api_key = settings.SKIDDLE_API_KEY
    page = request.GET.get('page', 1)
    items_per_page = 10

    response = requests.get(f"https://www.skiddle.com/api/v1/events/?api_key={api_key}&limit={items_per_page}&eventcode=FEST")
    data = response.json()

    events = data.get('results', [])
    paginator = Paginator(events, items_per_page)
    paginated_events = paginator.get_page(page)

    context = {
        'events': paginated_events,
    }
    return render(request, 'events/skiddle_festivals.html', context)


@login_required
def cancel_booking(request, event_id):
    """
        Cancel a booking for a specific event.

        This view allows the logged-in user to cancel their booking for a particular event. If the user has already
        booked a ticket for the event, the booking will be deleted, and a success message will be displayed. If no
        booking is found, an informational message is shown instead.

        Parameters:
        - request: The HTTP request object.
        - event_id: The primary key (id) of the event for which the user wishes to cancel their booking.

        Returns:
        - HTTP redirect to the user's profile page with appropriate success or info messages based on whether the
          booking was found and deleted.

        Template:
        - This view does not render a specific template, but it redirects to the user's profile after processing.
    """
    booking = Booking.objects.filter(user=request.user, event_id=event_id).first()

    if booking:
        booking.delete()
        messages.success(request, 'Your booking has been cancelled.')
    else:
        messages.error(request, 'Booking not found.')

    return redirect('profile')
