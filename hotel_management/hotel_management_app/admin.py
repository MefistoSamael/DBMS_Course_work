from django.contrib import admin
from django.utils.html import mark_safe

from .forms import (
    HotelFormForAdminPanel,
    InvoiceAdminForm,
    PaymentAdminForm,
    RoomImageFormForAdminPanel,
)
from .models import (
    Amenity,
    Booking,
    Feedback,
    Hotel,
    HotelFacility,
    Invoice,
    Payment,
    Room,
    RoomAmenity,
    RoomImage,
    UserActivityLog, Service, Event,
)
from .services import BookingService, HotelService, PaymentService, RoomImageService
from .services.invoice_service import InvoiceService
from .utils import save_model_admin_panel


class HotelAdmin(admin.ModelAdmin):
    form = HotelFormForAdminPanel
    readonly_fields = ("display_image",)

    def display_image(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="data:image/jpeg;base64,{obj.image}" style="max-width: 200px; max-height: 200px;" />'
            )
        return "No image"

    display_image.short_description = "Image"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["display_image"]
        return []

    def save_model(self, request, obj, form, change):
        save_model_admin_panel(form, obj, change, HotelService)


class RoomImageAdmin(admin.ModelAdmin):
    form = RoomImageFormForAdminPanel
    readonly_fields = ("display_image",)

    def display_image(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="data:image/jpeg;base64,{obj.image}" style="max-width: 200px; max-height: 200px;" />'
            )
        return "No image"

    display_image.short_description = "Image"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["display_image"]
        return []

    def save_model(self, request, obj, form, change):
        save_model_admin_panel(form, obj, change, RoomImageService)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    form = InvoiceAdminForm

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["is_paid"]
        return ["is_paid"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm

    def save_model(self, request, obj, form, change):
        if change:
            PaymentService.update(obj)
        else:
            PaymentService.create_payment(obj)

        invoice = obj.invoice
        total_payments = PaymentService.get_total_price_for_invoice(invoice.id)
        booking_total_price = BookingService.get_total_price_by_invoice_id(invoice.id)

        if total_payments >= booking_total_price:
            BookingService.update_is_paid(invoice.booking_id)

        if total_payments == invoice.total_amount:
            InvoiceService.update_is_paid(invoice.id)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["is_paid"]
        return ["is_paid"]


admin.site.register(RoomImage, RoomImageAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(HotelFacility)
admin.site.register(Room)
admin.site.register(Feedback)
admin.site.register(Amenity)
admin.site.register(RoomAmenity)
admin.site.register(UserActivityLog)
admin.site.register(Service)
admin.site.register(Event)
