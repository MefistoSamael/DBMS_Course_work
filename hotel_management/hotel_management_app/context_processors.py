from django.core.cache import cache

from .constants import DEFAULT_HOTEL_INFO
from .services import HotelService


def hotel_location(request):
    location = cache.get("hotel_location")
    if location is None:
        try:
            location = HotelService.get_first_hotel_location()
            cache.set("hotel_location", location)
        except Exception:
            location = DEFAULT_HOTEL_INFO.get("location", "")
    return {"hotel_location": location}
