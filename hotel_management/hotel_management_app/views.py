from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .constants import DEFAULT_HOTEL_INFO
from .forms import BookingForm
from .services import (
    AmenityService,
    BookingService,
    EventService,
    FeedbackService,
    HotelFacilityService,
    HotelService,
    RoomImageService,
    RoomService,
    ServiceService,
)
from .services.invoice_service import InvoiceService
from .services.user_activity_log_service import UserActivityLogService
from .utils import prepare_check_in_and_out_dates


def homepage(request):
    hotel_info = (
        HotelService.get_first_hotel_info_with_facilities() or DEFAULT_HOTEL_INFO
    )
    UserActivityLogService.log_action(
        user_id=request.user.id if request.user.is_authenticated else None,
        action_type="view",
        model_name="Hotel",
        object_id=hotel_info["id"],
        description="Viewed the homepage",
    )
    return render(request, "homepage.html", {"hotel_info": hotel_info})


def services(request):
    services_list = ServiceService.get_services_by_hotel_id()
    UserActivityLogService.log_action(
        user_id=request.user.id if request.user.is_authenticated else None,
        action_type="view",
        model_name="Services",
        description="Viewed services list",
    )
    return render(request, "services.html", {"services": services_list})


def room_list(request):
    filters = {
        "room_type": request.GET.get("room_type", ""),
        "capacity_min": request.GET.get("capacity_min", ""),
        "capacity_max": request.GET.get("capacity_max", ""),
        "price_min": request.GET.get("price_min", ""),
        "price_max": request.GET.get("price_max", ""),
        "is_available": request.GET.get("is_available", ""),
        "amenities": request.GET.getlist("amenities"),
        "sort_by": request.GET.get("sort_by", "number"),
        "sort_order": request.GET.get("sort_order", "asc"),
        "date_range": request.GET.get("date_range", ""),
    }

    page = int(request.GET.get("page", 1))
    limit = 10
    offset = (page - 1) * limit

    rooms = RoomService.get_filtered_rooms(filters, limit=limit, offset=offset)
    total_rooms = RoomService.get_filtered_rooms_count(filters)
    paginator = Paginator(range(total_rooms), limit)

    all_amenities = AmenityService.get_amenities_names_and_ids()

    UserActivityLogService.log_action(
        user_id=request.user.id if request.user.is_authenticated else None,
        action_type="view",
        model_name="Rooms",
        description="Viewed room list with filters",
    )
    return render(
        request,
        "rooms.html",
        {
            "rooms": rooms,
            "filters": filters,
            "all_amenities": all_amenities,
            "paginator": paginator,
            "page_obj": paginator.get_page(page),
            "current_date": timezone.now(),
        },
    )


def room_details(request, room_id):
    room = RoomService.get_room_details(room_id)

    if not room:
        return render(request, "404.html")

    average_rating = FeedbackService.get_average_room_rating(room_id)
    images = RoomImageService.get_all_room_images_by_room_id(room_id)
    amenities = AmenityService.get_all_amenities_by_room_id(room_id)
    feedback = FeedbackService.get_limit_feedbacks_by_room_id(room_id, 10)

    is_guest = request.user.is_authenticated and request.user.profile.role == "guest"
    is_admin = request.user.is_authenticated and request.user.profile.role == "admin"

    current_date = timezone.now()

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            date_range = form.cleaned_data["date_range"]
            check_in_date, check_out_date = prepare_check_in_and_out_dates(date_range)
            guest_id = request.user.profile.id

            try:
                booking_id = BookingService.create_booking(
                    guest_id, room_id, check_in_date, check_out_date
                )
                messages.success(request, "Booking created successfully!")
                UserActivityLogService.log_action(
                    user_id=request.user.id if request.user.is_authenticated else None,
                    action_type="create",
                    model_name="Booking",
                    object_id=booking_id,
                    description="User created a new booking",
                )
                return redirect("room_details", room_id=room_id)
            except Exception as e:
                messages.error(request, "Error creating booking: {}".format(str(e)))
        else:
            error_messages = "Invalid booking data. "
            for field, errors in form.errors.items():
                error_messages += f"{', '.join(errors)}"
            messages.error(request, error_messages)

    else:
        form = BookingForm()

    UserActivityLogService.log_action(
        user_id=request.user.id if request.user.is_authenticated else None,
        action_type="view",
        model_name="Room",
        object_id=room_id,
        description="Viewed room details",
    )

    context = {
        "room": room,
        "average_rating": average_rating,
        "images": images,
        "amenities": amenities,
        "feedback": feedback,
        "form": form,
        "is_guest": is_guest,
        "is_admin": is_admin,
        "current_date": current_date,
    }

    return render(request, "room_details.html", context)


def events_info(request):
    events = EventService.get_upcoming_events()
    context = {
        "events": events,
    }
    UserActivityLogService.log_action(
        user_id=request.user.id if request.user.is_authenticated else None,
        action_type="view",
        model_name="Events",
        description="User viewed events page",
    )
    return render(request, "events.html", context)


def facilities_list(request):
    facilities = HotelFacilityService.get_hotel_facilities(hotel_id=1)
    UserActivityLogService.log_action(
        user_id=request.user.id if request.user.is_authenticated else None,
        action_type="view",
        model_name="Facilities",
        description="User viewed facilities list",
    )
    return render(request, "facilities.html", {"facilities": facilities})


@login_required
def my_bookings(request):
    bookings = BookingService.get_user_bookings(request.user.profile.id)

    if request.method == "POST" and "cancel_booking" in request.POST:
        booking_id = request.POST.get("booking_id")
        BookingService.cancel_booking(booking_id)
        messages.success(request, "Booking canceled successfully")

        UserActivityLogService.log_action(
            user_id=request.user.id if request.user.is_authenticated else None,
            action_type="delete",
            model_name="Booking",
            object_id=booking_id,
            description="User canceled a booking",
        )
        return redirect("my_bookings")

    UserActivityLogService.log_action(
        user_id=request.user.id if request.user.is_authenticated else None,
        action_type="view",
        model_name="My Bookings",
        description="User viewed their bookings",
    )
    return render(
        request,
        "my_bookings.html",
        {"bookings": bookings, "today": timezone.now().date()},
    )


@login_required
def add_feedback(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        rating = request.POST.get("rating")
        comments = request.POST.get("comments")
        feedback_id = FeedbackService.add_feedback(
            request.user.profile.id, room_id, rating, comments
        )

        messages.success(request, "Feedback added successfully")

        UserActivityLogService.log_action(
            user_id=request.user.id if request.user.is_authenticated else None,
            action_type="create",
            model_name="Feedback",
            object_id=feedback_id,
            description="User added feedback",
        )
        return redirect("my_bookings")


@login_required
def invoice_details(request, booking_id):
    try:
        invoice_data = InvoiceService.get_invoice_details(booking_id)

        if not invoice_data:
            return render(request, "404.html")

        UserActivityLogService.log_action(
            user_id=request.user.id if request.user.is_authenticated else None,
            action_type="view",
            model_name="Invoice",
            object_id=(
                int(invoice_data.get("invoice_id"))
                if invoice_data.get("invoice_id")
                else None
            ),
            description="User viewed invoice details.",
        )
        return JsonResponse(invoice_data)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("my_bookings")
