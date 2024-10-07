from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    """
        Represents a category for events, such as "Music", "Sports", or "Arts".

        Fields:
            name (CharField): The name of the category (max length: 255).

        Methods:
            __str__: Returns the name of the category.
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Event(models.Model):
    """
        Represents an event in the system.

        Fields:
            title (CharField): The title of the event (max length: 255).
            description (TextField): The description of the event.
            date (DateTimeField): The date and time of the event.
            venue (CharField): The venue where the event takes place (max length: 255).
            city (CharField): The city where the event takes place (max length: 255).
            latitude (FloatField): The latitude of the event location (nullable, blank).
            longitude (FloatField): The longitude of the event location (nullable, blank).
            category (ForeignKey): The category of the event (related to Category model).
            organizer (ForeignKey): The user who organizes the event (related to User model).
            image (ImageField): An optional image for the event (uploads to 'event_images/').
            ticket_price (DecimalField): The price of a ticket for the event (max digits: 8, decimal places: 2).
            bookings_count (IntegerField): The count of how many bookings have been made for the event (default: 0).

        Methods:
            __str__: Returns the title of the event.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2)
    bookings_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Booking(models.Model):
    """
        Represents a booking made by a user for an event.

        Fields:
            user (ForeignKey): The user who made the booking (related to User model).
            event (ForeignKey): The event that was booked (related to Event model).
            booking_date (DateTimeField): The date and time when the booking was made (automatically set).

        Meta:
            unique_together (tuple): Ensures that a user can only book an event once.

        Methods:
            __str__: Returns a string representation of the booking, showing the user and the booked event.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} booked {self.event.title}"


class Review(models.Model):
    """
        Represents a review left by a user for an event.

        Fields:
            event (ForeignKey): The event being reviewed (related to Event model).
            user (ForeignKey): The user who left the review (related to User model).
            rating (IntegerField): The rating given by the user, between 1 and 5.
            comment (TextField): The user's comment on the event (optional).
            created_at (DateTimeField): The date and time the review was created (automatically set).

        Meta:
            unique_together (tuple): Ensures that a user can only review an event once.

        Methods:
            __str__: Returns a string representation of the review, showing the user and the event being reviewed.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"Review by {self.user.username} for {self.event.title}"


class SavedEvent(models.Model):
    """
        Represents an event that a user has saved for later viewing.

        Fields:
            user (ForeignKey): The user who saved the event (related to User model).
            event (ForeignKey): The event that was saved (related to Event model).
            saved_at (DateTimeField): The date and time when the event was saved (automatically set).

        Meta:
            unique_together (tuple): Ensures that a user can only save an event once.

        Methods:
            __str__: Returns a string representation of the saved event, showing the user and the saved event.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} saved {self.event.title}"