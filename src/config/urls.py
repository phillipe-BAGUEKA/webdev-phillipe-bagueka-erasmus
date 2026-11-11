"""First-slice pages, session actions and read-only catalogue API."""

from django.urls import path

from src.routes import auth, bookings, labs, pages

urlpatterns = [
    path("login", pages.login_page, name="login"),
    path("labs", pages.laboratories_page, name="laboratories"),
    path("api/labs", labs.laboratories_api, name="laboratories-api"),
    path("api/labs/<int:laboratory_id>/availability", bookings.availability_api,
         name="availability-api"),
    path("api/bookings", bookings.bookings_api, name="bookings-api"),
    path("api/bookings/<int:booking_id>/cancel", bookings.cancel_api,
         name="cancel-booking-api"),
    path("api/auth/login", auth.sign_in, name="sign-in"),
    path("api/auth/logout", auth.sign_out, name="sign-out"),
]
