from django.urls import path

from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("rooms/", views.room_list, name="rooms"),
    path("rooms/<int:room_id>/", views.room_details, name="room_details"),
    path("services/", views.services, name="services"),
    path("events/", views.events_info, name="events"),
    path("facilities/", views.facilities_list, name="facilities"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("add-feedback/", views.add_feedback, name="add_feedback"),
    path(
        "invoices/<int:booking_id>/details/",
        views.invoice_details,
        name="invoice_details",
    ),
]
