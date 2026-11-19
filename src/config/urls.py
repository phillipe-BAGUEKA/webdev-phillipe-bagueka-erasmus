"""Page, session and booking routes."""

from django.urls import path

from src.routes import ai_suggestion, auth, bookings, labs, pages, staff_bookings

urlpatterns = [
    path("login", pages.login_page, name="login"),
    path("labs", pages.laboratories_page, name="laboratories"),
    path("staff/bookings", staff_bookings.reservations_page, name="staff-bookings"),
    path("api/labs", labs.laboratories_api, name="laboratories-api"),
    path("api/labs/<int:laboratory_id>/availability", bookings.availability_api,
         name="availability-api"),
    path("api/labs/<int:laboratory_id>/suggestion", ai_suggestion.suggestion_api,
         name="suggestion-api"),
    path("api/bookings", bookings.bookings_api, name="bookings-api"),
    path("api/staff/bookings", staff_bookings.reservations_api, name="staff-bookings-api"),
    path("api/bookings/<int:booking_id>/cancel", bookings.cancel_api,
         name="cancel-booking-api"),
    path("api/auth/login", auth.sign_in, name="sign-in"),
    path("api/auth/logout", auth.sign_out, name="sign-out"),
]
