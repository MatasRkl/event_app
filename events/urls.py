from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='events/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update-email/', views.update_email, name='update_email'),
    path('profile/dashboard/', views.dashboard, name='dashboard'),
    path('profile/saved-events/', views.saved_events, name='saved_events'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/book/', views.book_ticket, name='book_ticket'),
    path('events/<int:id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:id>/delete/', views.delete_event, name='delete_event'),
    path('events/calendar/', views.event_calendar_view, name='event_calendar'),
    path('events/calendar/data/', views.event_calendar_data, name='event_calendar_data'),
    path('events/<int:event_id>/save/', views.save_event, name='save_event'),
    path('events/<int:event_id>/unsave/', views.unsave_event, name='unsave_event'),
    path('organizer/event/<int:event_id>/analytics/', views.event_analytics, name='event_analytics'),
    path('skiddle/popular/', views.skiddle_popular_events, name='skiddle_popular_events'),
    path('skiddle/festivals/', views.skiddle_festivals, name='skiddle_festivals'),
    path('cancel-booking/<int:event_id>/', views.cancel_booking, name='cancel_booking'),
]