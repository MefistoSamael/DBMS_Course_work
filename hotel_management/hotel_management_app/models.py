from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models


class BaseModel(models.Model):
    """Abstract base class with common fields for tracking creation, update, and deletion timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Hotel(BaseModel):
    """Hotel info"""

    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    image = models.TextField()

    def __str__(self):
        return self.name


class Room(BaseModel):
    """Room in the hotel"""

    ROOM_TYPE_CHOICES = (
        ("single", "Single"),
        ("double", "Double"),
        ("suite", "Suite"),
    )

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=False, blank=False)
    number = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            MinLengthValidator(1),
            RegexValidator(
                regex=r"^[A-Za-z0-9]+$", message="Room number must be alphanumeric."
            ),
        ],
    )
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    capacity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    is_available = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Room {self.number} ({self.room_type})"


class RoomImage(BaseModel):
    """Images of rooms"""

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.TextField()

    def __str__(self):
        return f"Image for room {self.room.number}"


class Booking(BaseModel):
    """Booking for rooms"""

    guest = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, limit_choices_to={"role": "guest"}
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.id} for {self.guest.user.username} in room {self.room.number}"


class Service(BaseModel):
    """Service provided by the hotel"""

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return self.name


class Invoice(BaseModel):
    """Invoice for a guest's stay"""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice for Booking {self.booking.id}"


class Payment(BaseModel):
    """Payment for an invoice"""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("cash", "Cash"),
            ("credit_card", "Credit Card"),
            ("bank_transfer", "Bank Transfer"),
        ],
    )

    def __str__(self):
        return f"Payment {self.id} for Invoice {self.invoice.id}"


class Amenity(BaseModel):
    """Amenities available in rooms (Wi-Fi, TV, Air Conditioning, etc.)"""

    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"


class RoomAmenity(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    def __str__(self):
        return f"Amenity {self.amenity.name} in room {self.room.number}"

    class Meta:
        verbose_name_plural = "Room Amenities"


class Feedback(BaseModel):
    """Guest feedback for the hotel"""

    guest = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, limit_choices_to={"role": "guest"}
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Feedback by {self.guest.user.username} for Room {self.room.id}"


class Event(BaseModel):
    """Events organized in the hotel (e.g. conferences, weddings)"""

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    description = models.TextField()
    event_date_from = models.DateField()
    event_date_to = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"Event: {self.name} on {self.event_date_from}"


class HotelFacility(BaseModel):
    """Hotel facilities (gym, pool, restaurant)"""

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    description = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Hotel Facilities"


class UserActivityLog(models.Model):
    """Journal for logging user actions in the system"""

    ACTION_CHOICES = (
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("view", "View"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} {self.action_type} {self.model_name} (ID: {self.object_id}) on {self.created_at}"

    class Meta:
        verbose_name = "User Activity Log"
        verbose_name_plural = "User Activity Logs"
        ordering = ["-created_at"]
