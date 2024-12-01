from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Booking, Hotel, Invoice, Payment, Room, RoomImage
from .services import BookingService
from .services.invoice_service import InvoiceService
from .services.payment_service import PaymentService
from .utils import clean_image, get_start_end_date


class HotelFormForAdminPanel(forms.ModelForm):
    image = forms.FileField(
        required=False,
        label="Choose Image",
        help_text="Allowed formats: jpg, jpeg, png, svg, webp",
    )

    class Meta:
        model = Hotel
        fields = "__all__"

    def clean_image(self):
        return clean_image(self.cleaned_data.get("image", ""))


class RoomImageFormForAdminPanel(forms.ModelForm):
    image = forms.FileField(
        required=False,
        label="Choose Image",
        help_text="Allowed formats: jpg, jpeg, png, svg, webp",
    )

    class Meta:
        model = RoomImage
        fields = "__all__"

    def clean_image(self):
        return clean_image(self.cleaned_data.get("image", ""))


class BookingForm(forms.ModelForm):
    date_range = forms.CharField(required=True)

    class Meta:
        model = Booking
        fields = ["date_range"]
        widgets = {
            "date_range": forms.TextInput(
                attrs={"type": "text", "placeholder": "Select Dates"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_range = cleaned_data.get("date_range")
        check_in_date, check_out_date = get_start_end_date(date_range)

        if (not check_in_date) or (not check_out_date):
            raise ValidationError("Please select a Check-in and Check-out dates")

        check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d").date()

        now = timezone.now()
        today = now.date()
        current_hour = now.hour

        if current_hour >= 10:
            if check_in_date <= today:
                raise ValidationError("Check-in date must be later than today date")
        else:
            if check_in_date < today:
                raise ValidationError("Check-in date must be today or later date")

        if check_out_date and check_in_date and check_out_date < check_in_date:
            raise ValidationError(
                "Check-out date must be on or after the check-in date"
            )

        return cleaned_data


class InvoiceAdminForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get("total_amount")
        booking = cleaned_data.get("booking")

        if total_amount and booking:
            booking_total_price = BookingService.get_total_price(booking.id)

            if total_amount < booking_total_price:
                raise ValidationError(
                    "Invoice total_amount cannot be less than the booking's total_price"
                )
        return cleaned_data


class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        amount_paid = cleaned_data.get("amount_paid")
        invoice = cleaned_data.get("invoice")

        if invoice and amount_paid:
            total_payments = PaymentService.get_total_price_for_invoice(invoice.id)

            new_total = total_payments + amount_paid
            invoice_total_amount = InvoiceService.get_total_amount(invoice.id)

            if new_total > invoice_total_amount:
                raise ValidationError(
                    "The total payments cannot exceed the invoice's total amount."
                )

        return cleaned_data
