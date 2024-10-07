from django.contrib import admin
from .models import Event, Category, Booking, Review

admin.site.register(Event)
admin.site.register(Category)
admin.site.register(Booking)
admin.site.register(Review)
