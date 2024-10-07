Event Management Application
This is a Django-based Event Management application where users can create, view, book, and cancel event bookings. The project includes a user profile section, event calendar, booking functionality, and event analytics tracking.

Features
User Profiles: Users can view and update their profiles.
Create Events: Users can create events, including setting a title, date, and location.
View Booked Events: Users can view all the events they have booked.
Cancel Bookings: Users can cancel their event bookings.
Event Calendar: A calendar view that displays all upcoming events.
Event Analytics: Track the number of bookings for each event.
Technologies Used
Python 3.x: Main programming language.
Django 4.x: Web framework used to develop the application.
SQLite3: Default database for development (ignored in Git via .gitignore).
Bootstrap 5: For styling the front-end.
FullCalendar.js: For rendering the calendar view of events.


Installation and Setup
1. Clone the repository:
    git clone https://github.com/MatasRkl/event_app.git

2. Create a virtual environment:
   python -m venv env

3. Activate the virtual environment:
    On Windows: .\env\Scripts\activate
    On Mac/Linux: source env/bin/activate

4. Install dependencies:
   pip install -r requirements.txt

5. Run database migrations:
    python manage.py migrate

6. Run the development server:
    python manage.py runserver



Usage
After registering or logging in, you can create events, book events, view your bookings, and cancel them.
Navigate to the Events Calendar to view upcoming events in a calendar format.
Admins can track event analytics and view the number of bookings for each event.
.gitignore
The .gitignore file is set up to exclude:

Database files (*.db, *.sqlite3).
Python cache files (__pycache__/, *.pyc).
Environment-specific files like .env (if used).